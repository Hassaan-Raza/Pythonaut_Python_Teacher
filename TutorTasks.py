from crewai import Task

def task_to_strings(task: Task):
    """Convert a Task object into (task, context) strings for DelegateWorkTool."""
    return (
        task.description.strip(),
        f"Expected output:\n{task.expected_output.strip()}" if task.expected_output else ""
    )

# -----------------------------
#  Teaching Task
# -----------------------------
# -----------------------------
#  Teaching Task
# -----------------------------
def teaching_task(topic, skill_level, student_background=""):
    # Define the proper learning progression for beginners
    python_progression = [
        "Variables and Data Types", "Strings and String Manipulation",
        "Numbers and Basic Operations", "Lists and Tuples", "Dictionaries and Sets",
        "Conditional Statements (if/elif/else)", "Loops (for/while)",
        "Functions", "Modules and Packages", "File Handling",
        "Error Handling (try/except)", "Object-Oriented Programming",
        "Advanced Topics (Decorators, Generators, etc.)"
    ]

    # If it's a beginner asking for general concepts, create a structured lesson
    if skill_level.lower() == "beginner" and any(
            word in topic.lower() for word in ["concept", "basics", "start", "beginner", "fundamental"]):
        progression_description = "\n".join([f"{i + 1}. {concept}" for i, concept in enumerate(python_progression)])

        return Task(
            description=f"""
            You are responsible for teaching Python programming to a complete beginner who wants to learn from the very basics.

            STUDENT PROFILE:
            - Skill Level: {skill_level}
            - Background: {student_background if student_background else 'No prior programming experience'}
            - Request: {topic}

            TEACHING APPROACH:
            Follow this structured progression for absolute beginners:
            {progression_description}

            REQUIREMENTS:
            1. Start with the absolute basics: what is programming, what is Python, and why learn it.
            2. Explain variables and data types with simple, relatable analogies.
            3. Cover string manipulation with practical examples.
            4. Progress through each concept in the order shown above.
            5. For each concept:
               - Provide a simple definition
               - Give a relatable analogy
               - Show 2-3 code examples that build understanding
               - Highlight common mistakes and how to avoid them
               - Suggest practical exercises
            6. Use plain, beginner-friendly language (avoid unnecessary jargon).
            7. If a technical term must be used, define it clearly.
            8. Keep explanations engaging and supportive.

            TONE & STYLE:
            - Patient, encouraging, and thorough
            - Start with simple explanations before adding complexity
            - Use everyday analogies that a complete beginner can relate to
            - Check for understanding with rhetorical questions
            """,
            expected_output=f"""
            A comprehensive beginner's guide to Python (Markdown format) that includes:

            PART 1: INTRODUCTION TO PROGRAMMING
            - What is programming and why learn Python?
            - Setting up a Python environment (brief overview)

            PART 2: CORE CONCEPTS (in order)
            For each of the following concepts, provide:
            - Clear definition with analogy
            - 2-3 progressively complex code examples
            - Common mistakes and how to avoid them
            - Practical mini-exercises

            Concepts to cover in order:
            {progression_description}

            PART 3: NEXT STEPS
            - How to practice effectively
            - Recommended learning resources
            - How to continue the learning journey

            The guide should be structured as a complete beginner's course that someone with no prior experience can follow.
            """,
            agent=None,
            output_file='beginner_python_course.md',
            config={},
        )
    else:
        # For specific topics or advanced students, use the original approach
        return Task(
            description=f"""
            You are responsible for teaching the Python topic **'{topic}'**.

            STUDENT PROFILE:
            - Skill Level: {skill_level}
            - Background: {student_background if student_background else 'Not provided'}

            REQUIREMENTS:
            1. Start with a **simple and clear definition** of the topic.
            2. Provide a **relatable analogy** that connects to everyday life.
            3. Create **2-3 progressively complex Python code examples** that build understanding step-by-step.
            4. Highlight **common mistakes and misconceptions** learners often make with this topic.
            5. Provide **practical applications** (real-world uses, mini-projects).
            6. Share **memory tips or strategies** to help the student retain the concept.
            7. Adjust the technical depth to match the student's **{skill_level}** level.

            TONE & STYLE:
            - Use plain, beginner-friendly language (avoid unnecessary jargon).
            - If a technical term must be used, **define it clearly**.
            - Keep explanations **engaging and supportive**.
            """,
            expected_output=f"""
            A comprehensive educational guide (Markdown format) that includes:
            - A clear **title** with the topic name.
            - A **definition** of the topic.
            - An **analogy**.
            - **Progressive code examples** (2-3).
            - A section on **common mistakes**.
            - A section on **practical applications**.
            - A section with **memory tips**.
            - A **summary** and **next learning steps**.
            """,
            agent=None,
            output_file='teaching_report.md',
            config={},
        )


# -----------------------------
#  Code Review Task
# -----------------------------
def code_review_task(code_snippet, skill_level, specific_concerns=""):
    return Task(
        description=f"""
        You are reviewing the following Python code for a **{skill_level}** level student:

        CODE TO REVIEW:
        ```python
        {code_snippet}
        ```

        Specific Concerns: {specific_concerns if specific_concerns else 'None provided'}

        REQUIREMENTS:
        1. Check **syntax and structure** for correctness.
        2. Evaluate **logic and efficiency**.
        3. Review **PEP 8 compliance** (readability, naming conventions, formatting).
        4. Assess **error handling and edge cases**.
        5. Identify opportunities to improve **readability and maintainability**.
        6. Provide **specific, actionable suggestions** for improvements.
        7. For each issue:
           - Explain why it’s problematic.
           - Show the corrected code.
           - Explain why the correction improves the code.
        8. Provide a **final corrected version** of the full code.

        TONE & STYLE:
        - Be constructive and encouraging (don’t overwhelm the student).
        - Explanations should be tailored for a **{skill_level}** student.
        - Prioritize the most important issues first.
        """,
        expected_output="""
        A structured code review (Markdown format) with:
        - **Overall assessment** (summary of strengths & weaknesses).
        - **Section-by-section analysis**.
        - A list of **issues with explanations**.
        - **Corrected code snippets** for each issue.
        - A **final corrected full code version**.
        - A list of **recommended resources** for further learning.
        """,
        agent=None,
        output_file='code_review.md',
        config={},
    )


# -----------------------------
#  Curriculum Design Task
# -----------------------------
def curriculum_task(student_goals, current_level, time_availability, specific_interests=""):
    return Task(
        description=f"""
        Design a personalized **Python learning curriculum**.

        STUDENT PROFILE:
        - Current Skill Level: {current_level}
        - Goals: {student_goals}
        - Time Availability: {time_availability}
        - Specific Interests: {specific_interests if specific_interests else 'Not provided'}

        REQUIREMENTS:
        1. Provide an **overall learning roadmap** with milestones.
        2. Break down the roadmap into **time-based segments** (weekly or monthly).
        3. Specify **topics to cover in each period**.
        4. Recommend **resources** (books, tutorials, documentation, videos).
        5. Assign **practice projects** for each major milestone.
        6. Include **assessment checkpoints** to track progress.
        7. Suggest strategies for **overcoming common learning plateaus**.
        8. Ensure the timeline is realistic for the given **{time_availability}**.

        TONE & STYLE:
        - Curriculum should balance **theory and practice**.
        - Recommend projects that match **student interests**.
        - Keep the plan **realistic and motivating**.
        """,
        expected_output="""
        A detailed learning plan (Markdown format) with:
        - **Overview** of the journey.
        - **Timeline** (weeks/months).
        - **Topics** for each period.
        - **Resources** for each topic.
        - **Practice projects** with descriptions.
        - **Assessment checkpoints**.
        - **Motivation tips** and advice for plateaus.
        """,
        agent=None,
        output_file='learning_plan.md',
        config={},
    )


# -----------------------------
#  Quiz Creation Task
# -----------------------------
def quiz_task(topic, skill_level, quiz_type="mixed"):
    return Task(
        description=f"""
        Create a **{quiz_type} quiz** on the topic **'{topic}'**.

        STUDENT PROFILE:
        - Skill Level: {skill_level}

        REQUIREMENTS:
        1. Include **5–8 questions** of varying difficulty.
        2. Use a mix of question types:
           - Multiple choice
           - Code output prediction
           - Bug identification
        3. Ensure questions are **clear and unambiguous**.
        4. For multiple choice:
           - Provide **plausible distractors**.
        5. Provide **detailed explanations** for correct answers.
        6. Explain **why incorrect answers are wrong**.
        7. Include a **scoring system or performance guide**.

        TONE & STYLE:
        - Keep questions **educational, not tricky**.
        - Match difficulty to **{skill_level}**.
        - Focus on **conceptual understanding** rather than rote memorization.
        """,
        expected_output="""
        A complete quiz (Markdown format) with:
        - **Title and instructions**.
        - Well-formatted **questions**.
        - **Answer choices** where relevant.
        - **Answer key with explanations**.
        - **Scoring guidelines**.
        - **Study recommendations** based on performance.
        """,
        agent=None,
        output_file='quiz.md',
        config={},
    )


# -----------------------------
#  Coordination Task
# -----------------------------
def coordination_task(context, student_query, student_level, student_goals):
    # Make sure context is always turned into a readable string
    if isinstance(context, list):
        context_str = "\n".join(context)
    else:
        context_str = str(context)

    return Task(
        description=f"""
        Coordinate the learning experience for a student with these characteristics:

        - Current query: {student_query}
        - Skill level: {student_level}
        - Learning goals: {student_goals}

        Conversation so far:
        {context_str}

        Your responsibilities:
        1. Decide which specialist agent(s) should handle this request.
        2. Assign specific tasks to each relevant agent.
        3. Maintain continuity with previous learning sessions.
        4. Ensure a cohesive and personalized learning experience.
        5. Synthesize multiple specialists' outputs if necessary.
        """,
        expected_output="""
        A coordination plan that includes:
        - Analysis of the student's query and needs
        - Decision on which specialist(s) to engage
        - Specific tasks to assign to each specialist
        - Context maintenance strategy
        - Plan for synthesizing multiple responses if needed
        - Next steps for the learning journey
        """,
        agent=None,
        output_file="coordination_plan.md",
        config={},
    )


def conversation_task(user_input, context=""):
    return Task(
        description=f"""
        Handle this casual conversation message from the student: "{user_input}"

        Context from previous messages: {context}

        Your goal is to respond naturally and keep the conversation flowing. This is not a technical 
        question about Python - it's casual conversation like greetings, thanks, or general chat.

        GUIDELINES:
        1. Keep responses brief and friendly
        2. Match the tone of the student's message
        3. If they say thanks, acknowledge it warmly
        4. If they greet you, respond appropriately
        5. If they make small talk, engage naturally
        6. Gently steer the conversation back to Python learning when appropriate
        7. Don't overthink it - keep it simple and human-like

        Remember: The student is interacting with a Python tutor, so keep your responses relevant 
        to the learning context while being natural and conversational.
        """,
        expected_output="A brief, friendly, natural conversation response (1-2 sentences max)",
        agent=None,
        output_file='conversation_log.md',
        config={},
    )