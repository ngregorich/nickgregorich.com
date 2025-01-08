---
title: "More uv and PG&E Plots"
date: 2025-01-07T08:02:15-08:00
description: ""
categories: []
tags: ["python", "uv", "streamlit", "pg&e", "energy", "plot"]
toc: true
math: false
draft: false
---
I continue to be super excited about the potential of [Astral uv](https://docs.astral.sh/uv/) being the one true way to charm Python (sorry JetBrains 🙂)

Previously, I [posted some quick benchmarks](https://www.nickgregorich.com/posts/uv-pip-docker-speed-up/) of a one line change from `pip` to `uv pip` in a Docker build. The performance increase was impressive and the level of effort left me thinking this must be too good to be true! But that was just scratching the surface of `uv`

# Goals

I wanted to demo starting a project from scratch with `uv` instead of just using `uv pip`. I also wanted to make the project something interesting enough that folks might be compelled to clone the repo and see how easy `uv` can make distributing a Python project

# The Demo

My `uv` demo needed to be something more interesting than a simple Python *Hello World*, but what could it be?

I am known to have an obsession with data – and data can make pretty (and pretty interactive) plots. That seems like it could be interesting

Part of my data obsession is being a [Streamlit](https://streamlit.io/) evangelist (although recently I did a project with [Plotly Dash](https://dash.plotly.com), which I should probably write about at some point). Not so coincidentally, Streamlit is a Python package that enables quick and easy generation of interactive dashboards (aka plots) via the web browser. Getting warmer!

I've spent a lot of time looking at my [PG&E](https://www.pge.com/) (that's Pacific Gas and Electric for those outside of the San Francisco Bay Area) energy data. I've never published any of my work – I think now's the time!

# The Result

I started a new Python project using the `uv` workflow, cleaned up my code, and wrote some documentation

The result can be found in this GitHub repo: [https://github.com/ngregorich/pge_plots/](https://github.com/ngregorich/pge_plots/)

Even if you don't have PG&E, you can pull the repo and follow the installation and usage instructions and see some plots

I hope that you have the same *WOW* reaction I did in how seamless the `uv` Python project distribution that I did 💫

Nick
