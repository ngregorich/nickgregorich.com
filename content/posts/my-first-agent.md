---
title: "My First Agent™"
date: 2026-03-22T14:14:59-07:00
description: ""
categories: []
tags: ["ai","llm","snowflake","sql","plotly"]
toc: true
math: false
draft: false
---
This was originally a part of my previous post, [It's Been A(I) While]({{< ref "/posts/its-been-ai-while" >}}), but it grew enough to warrant its own post

About this time last year I built my first agent, which took natural language questions about a fleet of IoT devices and effectively one-shotted into them into an interactive [Plotly Express](https://plotly.com/python/plotly-express/) chart

I built this tool after watching my colleagues, ranging from hardware engineers to business development folks to executives, juggle between ChatGPT and Visual Studio Code (OK maybe the execs weren't running VSCode). They always had their own (natural language) question in mind: How many devices were online this week and how does that compare to the previous week? What was the highest temperature recorded by each sensor in the last day? How many hours was the P50 / P75 / P90 cycle last night? They also had their end goal in mind: maybe a bar chart or box and whiskers or scatter plot to add to a presentation. To them, or maybe to most of us, the SQL itself was just a means to an end. So why not cut out the middle man and allow them to ask for the data they wanted in the form they wanted?

The data retrieved by this agent resided in [Snowflake](https://www.snowflake.com/) and the UI was built with [Streamlit](https://streamlit.io) (RIP Streamlit, but that's a post for another day). The magic for this tool was the context: the information beyond the database schema written by me after two and a half years working with the data. I hand wrote (this already sounds quaint) SQL for this database day in, day out. I knew what I could trust, what could be ignored, `WHERE` and when to `JOIN`, how to keep queries performant (an em dash would be nice here, but that era is gone), I knew every nook and cranny

I wrote it all down, similar to how you'd explain to a new hire but maybe a little more direct to save tokens. I explained everything down to the nuance of how `SYSDATE` works in Snowflake SQL versus other dialects. I don't remember how many tokens my context ended up needing, but I didn't need to integrate [RAG](https://en.wikipedia.org/wiki/Retrieval-augmented_generation) which really simplified the task

The agent used `chatgpt-4o-mini` which worked well most of the time but it could paint itself into a corner and iterate indefinitely. The tool was built as a state machine to divide up generating a SQL query, running the Snowflake query to retrieve the data, generating the UI, and displaying it. In order to prevent the LLM spinning its wheels and spending infinite tokens, I implemented a turn limit

I hosted the agent on [AWS Fargate](https://aws.amazon.com/fargate/) along with a number of other tools I had written. There's such a stark contrast between building a traditional tool or dashboard where you can test the happy path and build in guardrails to try and dull the sharp corners, and effectively shipping *SQL injection by design*™ (oh, that's a good one) and letting an LLM between your user and your database. I'm not sure that security has the same meaning 2026, but it seems like a good time to point out that it's wise to leverage Snowflake features like [roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview) and [statement timeout](https://docs.snowflake.com/en/sql-reference/parameters#statement-timeout-in-seconds)

It's exciting to release a tool like this and see if it gets any traction. It landed with the intended audience who quickly showed their questions and results. I was surprised and impressed to see a color-coded map of the United States in the first wave. I don't think I had ever used Plotly for maps nor did I often use state data myself, so to see a map beautifully shaded by sum of mass processed made me say: "Wow, I didn't know it could do that"

AI tools are often critiqued for their non-determinism and hallucinations, but they also expose deficiencies in data (and documentation) in record time. While the color-by-number map was a great use case of the agent, further investigation revealed that the states were stored as both abbreviation and full name and the plot was not aggregating over both. In this particular query, users would be mislead not because of the shortcomings of AI directly, but from the underlying dirty data. While this could happen to anyone querying this same data (by hand), seeing the underlying tables along the way would (hopefully) raise some flags. For example, seeing 100 or more rows of states (for the non-American reader there should only be 50). Don't underestimate the value of data cleanliness or documentation, even in the age of AI

Building the agent also reminded me of how critical it is to have a single source of truth. I found that the business side of the company had certain data definitions that they were aligned on and communicated out to partners, and they sometimes differed from the *well actually* semantically nuanced definitions that the engineering side might have. This is probably a tale as old as time, but when you throw an LLM in the mix it's hard to prevent those worlds from colliding. I thought of implementing a basic RAG that would use the username / group to draw from a business or engineering context, but that wasn't in the spirit of a single source of truth (and would have been more to maintain)

Usage of the tool continued to increase, which directly generated better understanding of our (actual) product. But there were indirect effects as well: people empowered to explore data seem more engaged and inspired, both in their role and the company but also in AI and tooling. During this critical phase, I made sure to make myself available for hand holding and feedback to increase adoption and make a better tool. As mentioned, although I tested against my personal workflows, when everything in the database is fair game every test case you can get your hands on makes a difference

I also saw a significant shift in my own work. Prior to my agent, a typical workflow might be writing SQL in [PyCharm's Database Tools](https://www.jetbrains.com/help/pycharm/relational-databases.html#first-steps), refining it, and dropping it into a Streamlit page as an overqualified Plotly Express host. My agent became my default workflow, though I would continue to peek at the generated SQL and result tables through the agent's debug mode. But this was definitely foreshadowing for what the next year would look ...

