import logging
from typing import Optional
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent

from app.classes.agent import AgentInfo, EvaluateAgentRequest, EvaluateAgentResponse
from app.services.agent.agent_service import AgentService
from app.services.tool.tool_service import ToolService
from app.services.chat.chat_service import ChatService
from app.core.config import settings
from app.utils.string.string_utils import is_empty_string
from app.utils.chat.chat_utils import convert_chat_messages
from agentevals.trajectory.match import create_trajectory_match_evaluator
from agentevals.trajectory.llm import create_trajectory_llm_as_judge, TRAJECTORY_ACCURACY_PROMPT, TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE


class AgentEvalService:
    """Service for evaluating agents"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(AgentEvalService, cls).__new__(cls)
        return cls._instance

    def _validate_evaluate_request(
        self, request: EvaluateAgentRequest
    ) -> tuple[bool, str]:
        """Validate evaluate agent request"""
        if is_empty_string(request.agent_id):
            return False, "Agent ID is required"
        
        if not request.input_messages or len(request.input_messages) == 0:
            return False, "Input messages are required"
        
        if not request.expected_trajectory or len(request.expected_trajectory) == 0:
            return False, "Expected trajectory is required"
        
        return True, ""


    async def evaluate_agent(
        self, request: EvaluateAgentRequest
    ) -> EvaluateAgentResponse:
        """
        Evaluate an agent by comparing expected vs actual trajectory.
        
        Args:
            request: EvaluateAgentRequest containing agent_id, input_messages, and expected_trajectory
            
        Returns:
            EvaluateAgentResponse with evaluation results
        """
        # Validate request
        valid, error_msg = self._validate_evaluate_request(request)
        if not valid:
            logging.getLogger("uvicorn.warning").warning(error_msg)
            return EvaluateAgentResponse(
                success=False,
                score=False,
                key="validation_error",
                comment=None,
                actual_trajectory=[],
                message=error_msg
            )

        try:
            # Step 1: Get agent
            logging.getLogger("uvicorn.info").info(f"Step 1: Getting agent {request.agent_id}")
            agent = await AgentService().get_agent(request.agent_id)
            model = ChatService().get_chat_model(agent.model)

            # Step 2: Load MCP tools
            logging.getLogger("uvicorn.info").info("Step 2: Loading MCP tools")
            functions = []
            if agent.tools is not None and len(agent.tools) > 0:
                functions = await ToolService().load_mcp_functions(agent.tools)

            # Step 3: Create LangGraph react agent
            logging.getLogger("uvicorn.info").info("Step 3: Creating LangGraph react agent")
            graph = create_react_agent(
                model,
                functions,
                prompt=await ChatService()._get_agent_system_prompt(agent),
            )

            # Step 4: Convert input messages to LangChain format
            logging.getLogger("uvicorn.info").info("Step 4: Converting input messages to LangChain format")
            initial_messages = convert_chat_messages(request.input_messages)

            # Step 5: Invoke the graph (without persisting to history)
            logging.getLogger("uvicorn.info").info("Step 5: Invoking graph to get actual trajectory")
            config = RunnableConfig(
                metadata={"evaluation": True},
                tags=[self.__class__.__name__],
                run_name=f"Evaluate {agent.name}",
            )
            result = await graph.ainvoke({"messages": initial_messages}, config=config)

            # Step 6: Convert actual trajectory to agentevals format
            logging.getLogger("uvicorn.info").info("Step 6: Converting trajectory to agentevals format")
            actual_trajectory = ChatService().jsonify_langchain_messages(
                result["messages"]
            )

            # Step 7: Create evaluator
            logging.getLogger("uvicorn.info").info("Step 7: Creating evaluator")
            if is_empty_string(request.judge_id):
                evaluator = create_trajectory_match_evaluator(
                    trajectory_match_mode=request.trajectory_match_mode.value,  
                    tool_args_match_mode=request.tool_args_match_mode.value,    
                    tool_args_match_overrides={}     
                )
            else:
                judge_model = ChatService().get_chat_model("gpt-4o-mini")
                evaluator = create_trajectory_llm_as_judge(
                    prompt=TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE,
                    judge=judge_model,
                )

            # Step 8: Evaluate
            logging.getLogger("uvicorn.info").info("Step 8: Evaluating")
            evaluation_result = evaluator(
                outputs=actual_trajectory,
                reference_outputs=request.expected_trajectory
            )

            # Step 9: Extract evaluation results
            logging.getLogger("uvicorn.info").info("Step 9: Extracting evaluation results")
            if isinstance(evaluation_result, dict):
                score = evaluation_result.get("score", False)
                key = evaluation_result.get("key", None)
                comment = evaluation_result.get("comment", None)
            else:
                score = False
                key = None
                comment = None
            
            # Convert score to bool if needed (handles float scores)
            if isinstance(score, (int, float)):
                score = bool(score)
            
            # Step 10: Return evaluation response
            logging.getLogger("uvicorn.info").info("Step 10: Returning evaluation response. Evaluation complete: score={score}, key={key}"
            )
            
            return EvaluateAgentResponse(
                success=True,
                score=bool(score),
                key=str(key),
                comment=str(comment) if comment else None,
                actual_trajectory=actual_trajectory,
                message="Evaluation completed successfully"
            )

        except Exception as e:
            error_msg = f"Failed to evaluate agent: {e}"
            logging.getLogger("uvicorn.error").error(error_msg)
            return EvaluateAgentResponse(
                success=False,
                score=False,
                key="error",
                comment=None,
                actual_trajectory=[],
                message=error_msg
            )

