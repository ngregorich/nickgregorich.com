---
title: "Amplify and git submodules"
date: 2024-01-20T18:23:26-08:00
description: "git submodules in Amplify"
categories: []
tags: ["hugo", "aws", "amplify", "git"]
toc: true
math: false
draft: true
---
I use a tool called [Hugo](https://gohugo.io) to publish this blog

Hugo is nice: you install it, choose (and maybe modify) a [theme](https://themes.gohugo.io) (I forked [TeXify3](https://github.com/ngregorich/hugo-texify3)), write [CommonMark markdown](https://spec.commonmark.org/current/) in a text editor of your choice, and run the command: `hugo` to generate a static website

You then host the generated static files on a [web server](https://gohugo.io/categories/hosting-and-deployment/) of your choice. I have some other projects running on [Amazon Web Services (AWS)](https://aws.amazon.com/), so I chose to host using [AWS Amplify](https://aws.amazon.com/amplify/)

Amplify is a set of services commonly used to support a web and / or mobile app. It includes [continuous integration / continuous deployment (CI / CD)](https://en.wikipedia.org/wiki/CI/CD), so it can automatically run the `hugo` command and generate updated static files each time the `main` branch of my [blog git repo](https://github.com/ngregorich/nickgregorich.com) is updated. This is a lot like [GitHub Actions](https://github.com/features/actions), which can help you [host Hugo with GitHub Pages](https://gohugo.io/hosting-and-deployment/hosting-on-github/)

I added my forked theme as a [git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) to my blog repo. I've used git submodules and their older cousins: [Mercurial subrepositories](https://wiki.mercurial-scm.org/Subrepository), and they can be quite contentious. They are a little complex and confusing which can lead to team frustration and a swift pivot to more of a [monorepo](https://en.wikipedia.org/wiki/Monorepo) setup

In the case of Amplify, using submodules can result in the following warning (which is really more of a fatal error given that your project can't build):
```
2022-08-02T16:23:43.814Z [WARNING]: # Unable to update submodules: Error: Command failed: git submodule update
                                    Cloning into '/codebuild/output/src964993672/src/amplify-app/src'...
                                    Host key verification failed.
                                    fatal: Could not read from remote repository.
                                    Please make sure you have the correct access rights
                                    and the repository exists.
```
This was reported in a [GitHub Issue](https://github.com/aws-amplify/amplify-hosting/issues/2904) in August 2022, but it still hasn't been resolved. I did a pivot of my own and included the theme source in my blog repo which got me deploying again, yay!

**tl;dr:** if you use AWS Amplify, you shouldn't use git submodules
