import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import type { ChatMessageInfo } from "@/components/chat/chat-message-info";

export interface MCPFunction {
    name: string;
    description: string | null;
    inputSchema: Record<string, any> | null;
    outputSchema: Record<string, any> | null;
}

export type TrajectoryMatch = "strict" | "unordered" | "superset" | "subset";
export type ToolArgsMatch = "ignore" | "exact" | "superset" | "subset";
export type MockedFunctionOutputs = Record<string, Record<string, any>>;

export interface ExpectedFunctionCall {
    id: string;
    function: MCPFunction;
    expectedInput: Record<string, any>;
}


export interface EvalResult {
    success: boolean;
    score: boolean; // True if trajectory matches, False otherwise
    key: string; // Evaluation key (e.g., "trajectory_strict_match")
    comment?: string; // Optional comment from evaluator
    actual_trajectory: Array<{
        role: string;
        content: string;
        tool_calls?: Array<{
            function: {
                name: string;
                arguments: string;
            };
        }>;
    }>;
    message: string;
}

// Single test case containing all evaluation data
export interface TestCase {
    id: string;
    name: string;
    messages: ChatMessageInfo[];
    llmAsJudge: boolean;
    trajectoryMatch: TrajectoryMatch;
    toolArgsMatch: ToolArgsMatch;
    expectedFunctionCalls: ExpectedFunctionCall[];
    mockedFunctionOutputs: MockedFunctionOutputs;
    evalResult: EvalResult | null;
}

// Test suite containing multiple test cases
export interface TestSuite {
    tests: TestCase[];
    selectedTestId: string | null;
}

const DEFAULT_MESSAGES: ChatMessageInfo[] = [
    {
        content: "Help me check system health?",
        role: "user",
    }
];

// Generate a unique ID for test cases
const generateTestId = () => `test-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

// Create a new default test case
const createDefaultTestCase = (name?: string): TestCase => ({
    id: generateTestId(),
    name: name || "Test 1",
    messages: [...DEFAULT_MESSAGES],
    llmAsJudge: false,
    trajectoryMatch: "strict",
    toolArgsMatch: "ignore",
    expectedFunctionCalls: [],
    mockedFunctionOutputs: {},
    evalResult: null,
});

type AgentEvalContextType = {
    // Test Suite Management
    testSuite: TestSuite;
    selectedTest: TestCase | null;
    selectTest: (testId: string) => void;
    addTest: (name?: string) => void;
    removeTest: (testId: string) => void;
    renameTest: (testId: string, name: string) => void;
    
    // Current Test Data (derived from selected test)
    messages: ChatMessageInfo[];
    setMessages: (messages: ChatMessageInfo[]) => void;
    addMessage: (content: string, role: "user" | "assistant") => void;
    resetMessages: () => void;
    selectedRole: "user" | "assistant";
    setSelectedRole: (role: "user" | "assistant") => void;
    llmAsJudge: boolean;
    setLlmAsJudge: (llmAsJudge: boolean) => void;
    trajectoryMatch: TrajectoryMatch;
    setTrajectoryMatch: (match: TrajectoryMatch) => void;
    toolArgsMatch: ToolArgsMatch;
    setToolArgsMatch: (match: ToolArgsMatch) => void;
    expectedFunctionCalls: ExpectedFunctionCall[];
    setExpectedFunctionCalls: (calls: ExpectedFunctionCall[]) => void;
    mockedFunctionOutputs: MockedFunctionOutputs;
    setMockedFunctionOutput: (functionName: string, output: Record<string, any>) => void;
    getMockedFunctionOutput: (functionName: string) => Record<string, any>;
    removeMockedFunctionOutput: (functionName: string) => void;
    evalResult: EvalResult | null;
    setEvalResult: (result: EvalResult | null) => void;
    
    // Reset entire suite
    resetSuite: () => void;
};

const AgentEvalContext = createContext<AgentEvalContextType | undefined>(undefined);

export const useAgentEval = () => {
    const context = useContext(AgentEvalContext);
    if (!context) {
        throw new Error("useAgentEval must be used within an AgentEvalProvider");
    }
    return context;
};

export const AgentEvalProvider = ({ children }: { children: ReactNode }) => {
    // Initialize with one default test
    const initialTest = createDefaultTestCase();
    const [testSuite, setTestSuite] = useState<TestSuite>({
        tests: [initialTest],
        selectedTestId: initialTest.id,
    });
    const [selectedRole, setSelectedRole] = useState<"user" | "assistant">("user");

    // Helper to update the selected test
    const updateSelectedTest = useCallback((updater: (test: TestCase) => TestCase) => {
        setTestSuite(prev => ({
            ...prev,
            tests: prev.tests.map(test => 
                test.id === prev.selectedTestId ? updater(test) : test
            ),
        }));
    }, []);

    // Test Suite Management
    const selectTest = useCallback((testId: string) => {
        setTestSuite(prev => ({
            ...prev,
            selectedTestId: testId,
        }));
    }, []);

    const addTest = useCallback((name?: string) => {
        const testNumber = testSuite.tests.length + 1;
        const newTest = createDefaultTestCase(name || `Test ${testNumber}`);
        setTestSuite(prev => ({
            tests: [...prev.tests, newTest],
            selectedTestId: newTest.id,
        }));
    }, [testSuite.tests.length]);

    const removeTest = useCallback((testId: string) => {
        setTestSuite(prev => {
            const filteredTests = prev.tests.filter(t => t.id !== testId);
            // If no tests left, create a new default one
            if (filteredTests.length === 0) {
                const newTest = createDefaultTestCase();
                return {
                    tests: [newTest],
                    selectedTestId: newTest.id,
                };
            }
            // If removed test was selected, select another one
            const newSelectedId = prev.selectedTestId === testId
                ? filteredTests[0].id
                : prev.selectedTestId;
            return {
                tests: filteredTests,
                selectedTestId: newSelectedId,
            };
        });
    }, []);

    const renameTest = useCallback((testId: string, name: string) => {
        setTestSuite(prev => ({
            ...prev,
            tests: prev.tests.map(test =>
                test.id === testId ? { ...test, name } : test
            ),
        }));
    }, []);

    // Current test data accessors
    const selectedTest = testSuite.tests.find(t => t.id === testSuite.selectedTestId) || null;
    const messages = selectedTest?.messages || [];
    const llmAsJudge = selectedTest?.llmAsJudge || false;
    const trajectoryMatch = selectedTest?.trajectoryMatch || "strict";
    const toolArgsMatch = selectedTest?.toolArgsMatch || "ignore";
    const expectedFunctionCalls = selectedTest?.expectedFunctionCalls || [];
    const mockedFunctionOutputs = selectedTest?.mockedFunctionOutputs || {};
    const evalResult = selectedTest?.evalResult || null;

    // Setters for current test
    const setMessages = useCallback((messages: ChatMessageInfo[]) => {
        updateSelectedTest(test => ({ ...test, messages }));
    }, [updateSelectedTest]);

    const setLlmAsJudge = useCallback((llmAsJudge: boolean) => {
        updateSelectedTest(test => ({ ...test, llmAsJudge }));
    }, [updateSelectedTest]);

    const setTrajectoryMatch = useCallback((trajectoryMatch: TrajectoryMatch) => {
        updateSelectedTest(test => ({ ...test, trajectoryMatch }));
    }, [updateSelectedTest]);

    const setToolArgsMatch = useCallback((toolArgsMatch: ToolArgsMatch) => {
        updateSelectedTest(test => ({ ...test, toolArgsMatch }));
    }, [updateSelectedTest]);

    const setExpectedFunctionCalls = useCallback((expectedFunctionCalls: ExpectedFunctionCall[]) => {
        updateSelectedTest(test => ({ ...test, expectedFunctionCalls }));
    }, [updateSelectedTest]);

    const setEvalResult = useCallback((evalResult: EvalResult | null) => {
        updateSelectedTest(test => ({ ...test, evalResult }));
    }, [updateSelectedTest]);

    const setMockedFunctionOutput = useCallback((functionName: string, output: Record<string, any>) => {
        updateSelectedTest(test => ({
            ...test,
            mockedFunctionOutputs: {
                ...test.mockedFunctionOutputs,
                [functionName]: output,
            },
        }));
    }, [updateSelectedTest]);

    const getMockedFunctionOutput = useCallback((functionName: string): Record<string, any> => {
        return mockedFunctionOutputs[functionName] || {};
    }, [mockedFunctionOutputs]);

    const removeMockedFunctionOutput = useCallback((functionName: string) => {
        updateSelectedTest(test => {
            const { [functionName]: _, ...rest } = test.mockedFunctionOutputs;
            return { ...test, mockedFunctionOutputs: rest };
        });
    }, [updateSelectedTest]);

    // Update selectedRole when messages updated (default behavior)
    useEffect(() => {
        const lastRole = messages.length > 0 ? messages[messages.length - 1].role : "assistant";
        const nextDefaultRole = lastRole === "user" ? "assistant" : "user";
        setSelectedRole(nextDefaultRole);
    }, [messages.length]);

    const addMessage = useCallback((content: string, role: "user" | "assistant") => {
        const newMessage: ChatMessageInfo = {
            content: content.trim(),
            role,
        };
        updateSelectedTest(test => ({
            ...test,
            messages: [...test.messages, newMessage],
        }));
    }, [updateSelectedTest]);

    const resetMessages = useCallback(() => {
        updateSelectedTest(test => ({
            ...test,
            messages: [...DEFAULT_MESSAGES],
            expectedFunctionCalls: [],
            mockedFunctionOutputs: {},
            evalResult: null,
        }));
    }, [updateSelectedTest]);

    const resetSuite = useCallback(() => {
        const newTest = createDefaultTestCase();
        setTestSuite({
            tests: [newTest],
            selectedTestId: newTest.id,
        });
    }, []);

    return (
        <AgentEvalContext.Provider
            value={{
                // Test Suite Management
                testSuite,
                selectedTest,
                selectTest,
                addTest,
                removeTest,
                renameTest,
                
                // Current Test Data
                messages,
                setMessages,
                addMessage,
                resetMessages,
                selectedRole,
                setSelectedRole,
                llmAsJudge,
                setLlmAsJudge,
                trajectoryMatch,
                setTrajectoryMatch,
                toolArgsMatch,
                setToolArgsMatch,
                expectedFunctionCalls,
                setExpectedFunctionCalls,
                mockedFunctionOutputs,
                setMockedFunctionOutput,
                getMockedFunctionOutput,
                removeMockedFunctionOutput,
                evalResult,
                setEvalResult,
                
                // Reset Suite
                resetSuite,
            }}
        >
            {children}
        </AgentEvalContext.Provider>
    );
};
