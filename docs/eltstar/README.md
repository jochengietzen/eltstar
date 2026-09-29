---
icon: simple/markdown
---

# eltstar

## WTF - W Questions
### Why did we create this library?
We (Tim and Jochen) created eltstar after several years in the ("modern") data engineering industry. There are many things we like and surely as many things that frustrate us. 
A few of the biggest issues we try to solve using this library. Some of them being

- Vendor Lock-In and difficulty of switching between - well anything. It is relatively hard to move your code from databricks to snowflake (or vice versa) or simply from pandas to pyspark.
- We are tired of choosing spark over e.g. polars to be future proof, while we deal with industries that are likely never going to hit any rates, that justify the sledgehammer to crack the few tens to hundreds of Gigabytes found in a large portion of industries.
- The landscape of data engineering is growing and growing - for better AND for worse. Keeping an overview of every way to model your pipelines and the damn boilerplate that happens in every system or vendor is unnecessary repetition and a perfect source to introduce bugs.
- The lack of testing in elt/etl products is shocking. But we understand why - it can be hard. We won't be able to solve everything here, but we tackle a lot in that area.
- Additionally to your data frame library, you need to get into details for testing and data quality checks.

The list can easily be continued, but these were the most mentionable for our case.

We try to tackle these things by unifying the ideas we like into a (hopefully) simplified syntax/semantic.

### Who is this for?
We don't want to solve everything for everyone. Our focus is to help the persons/companies simplifying their elt setup for fairly standard cases. 

- You want to build up a data lake architecture like the known 3-layer architecture (however way you want to name it)?
- You want to load data from external sources or even send data to external systems?
- You want to be able to smoke test your transformations locally instead of running even on a dev stage?
- You are just starting out and would like to start with something lightweight like polars but don't want to loose the possibility to switch to another library like spark later on?
- You are able to define your tables beforehand and type them properly?

### Who is this NOT for?

- If you are in an environment, where your elt structure is very dynamic and you cannot define your table structure in advance, this is not the product for you.
- ... tbc.

### What is this library trying to achieve?

- Standardising the way you model your elt pipelines.
