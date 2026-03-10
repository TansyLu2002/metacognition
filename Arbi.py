import pandas as pd
import streamlit as st


st.set_page_config(page_title="Metacognitive Regulation Tool", layout="wide")
st.title("AI-Supported Metacognitive Regulation Tool")

# --------------------------
# Constants
# --------------------------
PROBLEMS = ["Arbitrage", "Hawker Center"]

YES_NO_OPTIONS = ["No", "Yes"]

DECISION_OPTIONS = [
    "Accept and use it",
    "Revise the prompt and ask again",
    "Keep part of it, reject part of it",
    "Try a different strategy (with or without AI)",
    "Pause and rethink the task itself before continuing",
]

PLANNING_HINT_TEXT = """Hints: Possible planning stages

Build a mathematical model
Translate the problem into a mathematical form before trying to solve it. For example, think about how the exchange-rate table can be represented mathematically, what condition would indicate a multi-currency arbitrage opportunity, and how the gain along a sequence of currency exchanges should be calculated.

Choose a solution strategy
After building the model, decide how you want to solve the problem. For example, consider whether you want to test a few cycles manually, search systematically for possible arbitrage cycles, treat the problem as a graph problem, or transform the multiplicative relationships into a form that is easier to analyse.

Implement the method in code
Use your mathematical model and chosen strategy to guide your coding. For example, think about how to store the exchange-rate data, how to represent the structure of the problem in code, how to implement your detection method, and what output your program should produce.

Check and validate the result
Do not assume that a computed result is automatically correct. Check whether the output is consistent with your mathematical model, whether a detected path really produces arbitrage, and whether a failure to detect arbitrage reflects the actual problem rather than an issue in the code or method.

Interpret and present the solution
Finally, explain clearly what your result means. State whether an arbitrage opportunity exists, what evidence supports your conclusion, and how your mathematical model, code output, and final interpretation connect to one another.
"""

TASK_HINTS = {
    1: """Hint for Task 1: Build a Mathematical Model

At this stage, focus on translating the problem into a mathematical form before coding. Think about what each exchange rate means, how to represent a currency conversion mathematically, and what condition would indicate arbitrage.

You may find it helpful to define:

aij: the exchange rate from currency i to currency j
xij: the amount of currency i converted to currency j
yk: the net amount of currency k after all transactions

Then ask yourself:

What objective should be maximized?
How should the flow-balance constraints be written?
How can the model indicate whether arbitrage exists?

One possible way to think about the problem is to use aij, xij, and yk to describe exchange rates, transaction flows, and net outcomes, and then consider whether the model can produce a profitable closed cycle of exchanges.""",

    2: """Hint for Task 2: Choose a Solution Strategy

Once your mathematical model is clear, the next step is to decide how you want to solve the problem. Try not to move directly to coding before you have chosen a method.

You may find it helpful to think about questions such as:

Do I want to solve this as an optimisation problem, a graph problem, or another type of problem?
What should my method take as input, and what should it return as output?
If arbitrage exists, how will I identify the profitable cycle or path?
How can I make sure that my method matches the mathematical model I built?""",

    3: """Hint for Task 3: Implement the Method in Code

Now use your mathematical model and chosen strategy to guide your coding. Try to keep the code aligned with your own reasoning, rather than writing code first and hoping it works.

A useful coding plan may include:

loading or storing the exchange-rate data clearly
writing a function to detect whether arbitrage exists
writing a second function, if needed, to recover the arbitrage path or cycle
testing your code on the given exchange-rate table

You do not need to follow this structure exactly, but it may help you think about how to separate the problem into clear coding steps. As you code, keep asking yourself whether each part of the program corresponds to something meaningful in your mathematical model.

Example code skeleton:
from gurobipy import Model, GRB, quicksum
import numpy as np

def arbitrage_detection(rates):
    # build the model here
    # define decision variables
    # set the objective
    # add the constraints
    # solve the model
    pass

def find_the_path(x_opt_indices):
    # reconstruct a path from the nonzero decisions
    pass

Example of loading the rate matrix:

import pandas as pd
rates_df = pd.read_csv("arbitrage.csv")
rates = rates_df.values[:, 1:]  # adjust this if needed""",

    4: """Hint for Task 4: Check and Validate the Result

After you obtain a result, do not assume that it is automatically correct. Your next job is to check whether the output really matches the mathematical meaning of arbitrage.

You may find it helpful to ask:

Does my code say that arbitrage exists or not?
If arbitrage exists, does the reported path or cycle actually make sense?
If I multiply the exchange rates along that cycle, do I really end up with more than I started with?
If no arbitrage is found, could that be due to a problem in my code or method rather than the data itself?

Example validation idea:
if all_one:
    arbitrage_path = find_the_path(np.argwhere(x_opt))
    print("Arbitrage path is:", arbitrage_path)

You may also try a simple manual check on one reported path to confirm that the result is consistent with your model and code.""",

    5: """Hint for Task 5: Interpret and Present the Solution

In this task, do not only report the code output. Explain what the result means in relation to the original problem and how your conclusion is supported by both the model and the computation.

A clear final explanation may include:

whether an arbitrage opportunity exists
if yes, what the profitable path or cycle is
why that path creates profit
if no arbitrage is found, what evidence supports that conclusion
how your mathematical model, code output, and interpretation connect to one another

Try to present your solution in a way that makes your reasoning visible, rather than only stating the final answer.""",
}

GENERIC_TASK_HINT = """General hint for this task

At this stage, focus on keeping your work aligned with your own task plan and reasoning.

You may find it helpful to ask:

What exactly is this task trying to achieve?
How does this task connect to my earlier model, method, or result?
What kind of AI support do I actually need here: explanation, options, checking, debugging, or interpretation?
What part of this task should still remain my responsibility?
How will I know whether the output is valid, useful, and relevant to the problem?

Try to make sure that:
- your task goal is clear,
- your prompt asks for specific help,
- your evaluation checks the response critically,
- and your next step follows from evidence rather than convenience.
"""


# --------------------------
# Helpers
# --------------------------
def key_prefix(problem: str) -> str:
    return problem.lower().replace(" ", "_")


def get_hint(decision: str) -> str:
    if decision == "Revise the prompt and ask again":
        return "Hint: Make the prompt more specific and ask only for the kind of help you actually need."
    if decision == "Try a different strategy (with or without AI)":
        return "Hint: Consider whether the task should be split differently or whether another representation would work better."
    if decision == "Pause and rethink the task itself before continuing":
        return "Hint: Revisit the task goal and check whether this is the right subproblem to work on now."
    return ""


def get_task_hint_text(task_no: int) -> str:
    if task_no in TASK_HINTS:
        return TASK_HINTS[task_no]
    return GENERIC_TASK_HINT


def init_problem_state(problem: str) -> None:
    p = key_prefix(problem)

    defaults = {
        f"{p}_num_tasks": 2,
        f"{p}_planning_intro": "",
        f"{p}_a1_task_decomposition": "",
        f"{p}_h1_need_planning_hint": "No",
        f"{p}_h1_planning_hint_notes": "",
        f"{p}_a2_role_ai_role": "",
        f"{p}_final_reflection": "",
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def init_task_state(problem: str, task_no: int) -> None:
    p = key_prefix(problem)
    prefix = f"{p}_task_{task_no}"

    defaults = {
        f"{prefix}_title": "",
        f"{prefix}_step1_define": "",
        f"{prefix}_need_hint": "No",
        f"{prefix}_hint_notes": "",
        f"{prefix}_step2_prompt_eval": "",
        f"{prefix}_step3_decision": DECISION_OPTIONS[0],
        f"{prefix}_step3_notes": "",
        f"{prefix}_step4_implement_test_interpret": "",
        f"{prefix}_revise_from_beginning": "No",
        f"{prefix}_step5_revise": "",
        f"{prefix}_step6_reflect": "",
        f"{prefix}_saved": False,
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# --------------------------
# Session state initialization
# --------------------------
if "started" not in st.session_state:
    st.session_state.started = False

for problem in PROBLEMS:
    init_problem_state(problem)
    p = key_prefix(problem)
    for i in range(1, st.session_state.get(f"{p}_num_tasks", 2) + 1):
        init_task_state(problem, i)


# --------------------------
# Export
# --------------------------
def export_dataframe() -> pd.DataFrame:
    rows = []

    for problem in PROBLEMS:
        p = key_prefix(problem)
        num_tasks = st.session_state.get(f"{p}_num_tasks", 0)

        rows.append(
            {
                "problem": problem,
                "section": "planning",
                "task_no": "",
                "planning_intro": st.session_state.get(f"{p}_planning_intro", ""),
                "a1_task_decomposition": st.session_state.get(f"{p}_a1_task_decomposition", ""),
                "h1_need_planning_hint": st.session_state.get(f"{p}_h1_need_planning_hint", ""),
                "h1_planning_hint_notes": st.session_state.get(f"{p}_h1_planning_hint_notes", ""),
                "a2_role_ai_role": st.session_state.get(f"{p}_a2_role_ai_role", ""),
                "task_title": "",
                "step1_define": "",
                "need_hint": "",
                "hint_notes": "",
                "step2_prompt_eval": "",
                "step3_decision": "",
                "step3_notes": "",
                "step4_implement_test_interpret": "",
                "revise_from_beginning": "",
                "step5_revise": "",
                "step6_reflect": "",
                "final_reflection": "",
            }
        )

        for i in range(1, num_tasks + 1):
            prefix = f"{p}_task_{i}"
            init_task_state(problem, i)

            rows.append(
                {
                    "problem": problem,
                    "section": "task",
                    "task_no": i,
                    "planning_intro": "",
                    "a1_task_decomposition": "",
                    "h1_need_planning_hint": "",
                    "h1_planning_hint_notes": "",
                    "a2_role_ai_role": "",
                    "task_title": st.session_state.get(f"{prefix}_title", ""),
                    "step1_define": st.session_state.get(f"{prefix}_step1_define", ""),
                    "need_hint": st.session_state.get(f"{prefix}_need_hint", ""),
                    "hint_notes": st.session_state.get(f"{prefix}_hint_notes", ""),
                    "step2_prompt_eval": st.session_state.get(f"{prefix}_step2_prompt_eval", ""),
                    "step3_decision": st.session_state.get(f"{prefix}_step3_decision", ""),
                    "step3_notes": st.session_state.get(f"{prefix}_step3_notes", ""),
                    "step4_implement_test_interpret": st.session_state.get(f"{prefix}_step4_implement_test_interpret", ""),
                    "revise_from_beginning": st.session_state.get(f"{prefix}_revise_from_beginning", ""),
                    "step5_revise": st.session_state.get(f"{prefix}_step5_revise", ""),
                    "step6_reflect": st.session_state.get(f"{prefix}_step6_reflect", ""),
                    "final_reflection": "",
                }
            )

        rows.append(
            {
                "problem": problem,
                "section": "reflection",
                "task_no": "",
                "planning_intro": "",
                "a1_task_decomposition": "",
                "h1_need_planning_hint": "",
                "h1_planning_hint_notes": "",
                "a2_role_ai_role": "",
                "task_title": "",
                "step1_define": "",
                "need_hint": "",
                "hint_notes": "",
                "step2_prompt_eval": "",
                "step3_decision": "",
                "step3_notes": "",
                "step4_implement_test_interpret": "",
                "revise_from_beginning": "",
                "step5_revise": "",
                "step6_reflect": "",
                "final_reflection": st.session_state.get(f"{p}_final_reflection", ""),
            }
        )

    return pd.DataFrame(rows)


# --------------------------
# Render sections
# --------------------------
def render_plan(problem: str) -> None:
    p = key_prefix(problem)

    st.subheader("Plan")

    with st.expander("Part A: Plan Before You Ask AI", expanded=True):
        st.text_area(
            "Before using AI, take time to break the problem into smaller tasks.",
            key=f"{p}_planning_intro",
            height=100,
            placeholder="Write your planning notes here...",
        )

    with st.expander("A1. Task Decomposition", expanded=True):
        st.markdown(
            """
Before using AI, break the problem into a set of smaller tasks that you think are needed.

- What smaller tasks do I need to complete to solve this problem?
- In what order should I attempt them?
- Which tasks are about understanding/modeling, checking/calculation, proof/justification, or interpretation?
"""
        )
        st.text_area(
            "Write your task list here:",
            key=f"{p}_a1_task_decomposition",
            height=180,
            placeholder="1.\n2.\n3.\n...",
        )

    with st.expander("H1. Do you need hints for the planning stage?", expanded=False):
        st.radio(
            "Do you need hints for the planning stage?",
            YES_NO_OPTIONS,
            key=f"{p}_h1_need_planning_hint",
            horizontal=True,
        )

        if st.session_state.get(f"{p}_h1_need_planning_hint", "No") == "Yes":
            st.info(PLANNING_HINT_TEXT)
            st.text_area(
                "Planning hint notes",
                key=f"{p}_h1_planning_hint_notes",
                height=120,
                placeholder="Write any useful planning notes here...",
            )

    with st.expander("A2. My Role and AI's Role", expanded=True):
        st.markdown(
            """
Before using AI, think about how you want to share the work across the process.

- What should I be responsible for?
- What can AI help with?
- What should I not delegate to AI?
"""
        )
        st.text_area(
            "My role and AI's role",
            key=f"{p}_a2_role_ai_role",
            height=180,
            placeholder="Write here...",
        )


def render_task(problem: str, task_no: int) -> None:
    p = key_prefix(problem)
    prefix = f"{p}_task_{task_no}"

    init_task_state(problem, task_no)

    task_header = "Monitor Task 1" if task_no == 1 else f"Task {task_no}"
    st.subheader(task_header)

    with st.expander(f"Task {task_no}: Your Planned Task", expanded=True):
        st.text_area(
            f"Task {task_no}: Now focus on Task {task_no} from the task plan you created in Part A.",
            key=f"{prefix}_title",
            height=110,
            placeholder=f"Describe what Task {task_no} is.",
        )

    with st.expander("Step 1. Define This Task", expanded=True):
        st.text_area(
            "Focus on this task from your own plan. Before using AI, first make clear what you are trying to do.",
            key=f"{prefix}_step1_define",
            height=140,
            placeholder="Define this task clearly here...",
        )

    with st.expander(f"Do you need hints for Task {task_no}?", expanded=False):
        st.radio(
            f"Do you need hints for Task {task_no}?",
            YES_NO_OPTIONS,
            key=f"{prefix}_need_hint",
            horizontal=True,
        )

        if st.session_state.get(f"{prefix}_need_hint", "No") == "Yes":
            st.info(get_task_hint_text(task_no))
            st.text_area(
                "Hint notes",
                key=f"{prefix}_hint_notes",
                height=120,
                placeholder="Write any useful notes from the hint here...",
            )

    with st.expander("Step 2. Prompt AI and Evaluate the Response", expanded=False):
        st.text_area(
            "Write a prompt to AI for this specific task. After receiving AI's response, evaluate it critically.",
            key=f"{prefix}_step2_prompt_eval",
            height=180,
            placeholder="Write your prompt, summarize the AI response, and evaluate it here...",
        )

    with st.expander("Step 3. Decide What to Do Next", expanded=False):
        st.radio(
            "Based on your evaluation of AI's response, decide what you will do next.",
            DECISION_OPTIONS,
            key=f"{prefix}_step3_decision",
        )
        st.text_area(
            "Decision notes",
            key=f"{prefix}_step3_notes",
            height=100,
            placeholder="Explain why you made this decision...",
        )

        hint_text = get_hint(st.session_state.get(f"{prefix}_step3_decision", ""))
        if hint_text:
            st.info(hint_text)

    with st.expander("Step 4. Implement, Test, and Interpret", expanded=False):
        st.text_area(
            "Now apply the idea, method, or response that you decided to use. Record what you did and what happened.",
            key=f"{prefix}_step4_implement_test_interpret",
            height=180,
            placeholder="Describe implementation, observed results, and interpretation...",
        )

    with st.expander(
        "Based on my evaluation of the result, do I need to revise this task from the beginning?",
        expanded=False,
    ):
        st.radio(
            "Do I need to revise this task from the beginning?",
            YES_NO_OPTIONS,
            key=f"{prefix}_revise_from_beginning",
            horizontal=True,
        )

    if st.session_state.get(f"{prefix}_revise_from_beginning", "No") == "Yes":
        with st.expander("Step 5. Revise if Needed", expanded=True):
            st.text_area(
                "If the response, method, or result was not fully satisfactory, revise your prompt or approach here.",
                key=f"{prefix}_step5_revise",
                height=140,
                placeholder="Write revisions here...",
            )

    with st.expander("Step 6. Reflect on This Task", expanded=False):
        st.text_area(
            "Finally, reflect on what you learned from this task.",
            key=f"{prefix}_step6_reflect",
            height=140,
            placeholder="Write your reflection here...",
        )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Save task", key=f"{prefix}_save_btn", use_container_width=True):
            st.session_state[f"{prefix}_saved"] = True
    with col2:
        if st.session_state.get(f"{prefix}_saved", False):
            st.success(f"{problem} - Task {task_no} saved.")


def render_reflection(problem: str) -> None:
    p = key_prefix(problem)

    st.subheader("Reflection")
    st.text_area(
        "Part C: End-of-Problem Reflection\n\nNow that you have completed all of your tasks, take some time to reflect on your overall process.",
        key=f"{p}_final_reflection",
        height=260,
        placeholder="Write your end-of-problem reflection here...",
    )


# --------------------------
# Sidebar
# --------------------------
with st.sidebar:
    st.header("Controls")

    if st.session_state.started:
        for problem in PROBLEMS:
            p = key_prefix(problem)
            if st.button(f"+ Add Task to {problem}", key=f"add_{p}", use_container_width=True):
                st.session_state[f"{p}_num_tasks"] += 1
                init_task_state(problem, st.session_state[f"{p}_num_tasks"])
                st.rerun()

    df_export = export_dataframe()
    csv_bytes = df_export.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name="metacognition_results.csv",
        mime="text/csv",
        use_container_width=True,
    )

    if st.session_state.started:
        for problem in PROBLEMS:
            p = key_prefix(problem)
            st.caption(f"{problem}: {st.session_state[f'{p}_num_tasks']} task(s)")
    else:
        st.caption("Please start from the welcome page.")


# --------------------------
# Welcome page
# --------------------------
if not st.session_state.started:
    st.markdown("## Welcome")
    st.markdown(
        """
You are not solving the whole problem at once. Your job is to manage your thinking while using AI as a tool.

### Your goals are to:
- break a complex problem into your own tasks,
- decide what you should do vs what AI should do,
- use AI iteratively within each task,
- evaluate AI outputs critically,
- implement and test proposed solutions,
- and revise both your prompts and your task plan when needed.

### In this activity
You will work on two independent problems:

- **Arbitrage**
- **Hawker Center**

For each problem, you will complete:

- **Part A: Planning**
- **Part B: One or more task cycles**
- **Part C: End-of-problem reflection**

You may complete the two problems in any order.

You must click Start before accessing the rest of the app.
        """
    )

    if st.button("Start", type="primary", use_container_width=True):
        st.session_state.started = True
        st.rerun()

else:
    main_tabs = st.tabs(PROBLEMS)

    for idx, problem in enumerate(PROBLEMS):
        p = key_prefix(problem)
        num_tasks = st.session_state.get(f"{p}_num_tasks", 2)

        with main_tabs[idx]:
            st.header(problem)
            st.caption("This problem is independent. You do not need to complete the other one first.")

            section_labels = ["Plan"] + [f"Task {i}" for i in range(1, num_tasks + 1)] + ["Reflection"]
            inner_tabs = st.tabs(section_labels)

            with inner_tabs[0]:
                render_plan(problem)

            for i in range(1, num_tasks + 1):
                with inner_tabs[i]:
                    render_task(problem, i)

            with inner_tabs[-1]:
                render_reflection(problem)

    st.divider()
    st.subheader("Preview of export data")
    st.dataframe(export_dataframe(), use_container_width=True)