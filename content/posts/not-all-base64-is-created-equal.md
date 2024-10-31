---
title: "Not all Base64 is created equal"
date: 2024-10-30T17:17:22-07:00
description: ""
categories: []
tags: ["python", "web"]
toc: true
math: false
draft: false
---
TIL not all [Base64](https://en.wikipedia.org/wiki/Base64) encoding is created equal

I have a fun, kind of hacky project where I wanted to be able to embed a SQL query in a URL

Since I knew that `%` was a [reserved character](httpsq://en.wikipedia.org/wiki/Percent-encoding#Types_of_URI_characters) in a URL and that we're very likely to see a `%` in our SQL queries in the form of a `LIKE '%statement%'`, I decided to use Base64 encoding on the query string

Python [`base64.b64encode`](https://docs.python.org/3/library/base64.html#base64.b64encode) and [`base64.b64decode`](https://docs.python.org/3/library/base64.html#base64.b64decode) to the rescue!

This works, until it doesn't ☹️

The problem with this solution is that `b64encode` **does not** output URL safe bytes, at least not all the time. The default [RFC 4648](https://datatracker.ietf.org/doc/html/rfc4648#section-4) output includes `+` and `/` which are *both* URL reserved characters

If you try to decode "base64 encoded" bytes from a URL using these methods, you might see an error like:

`Invalid base64-encoded string: number of data characters (<number>) cannot be 1 more than a multiple of 4`

Luckliy the [next section of RFC 4648](https://datatracker.ietf.org/doc/html/rfc4648#section-5) describes Base64 encoding with a URL and filename safe alphabet, which swaps `+` with `-` and `/` with `_`

Even luckier, the python `base64` package also includes functions for this section of the RFC: `urlsafe_b64encode` and `urlsafe_b64decode`

If you have even more specific needs, you can check out the `altchars=` parameter of the [`base64.b64encode`](https://docs.python.org/3/library/base64.html#base64.b64encode) and [`base64.b64decode`](https://docs.python.org/3/library/base64.html#base64.b64decode) functions
