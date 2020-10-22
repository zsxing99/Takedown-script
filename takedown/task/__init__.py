"""
task submodule v0.0.1

This submodule is a collections of the take down tasks.

Tasks are listed below:
1. Run tool to find repos that should be taken down
    Tool should group repos by owner, if one owner has multiple repos in violation
    Newly found repos are tagged as “new”
2. Manually associate repo owners with one or multiple email addresses
    Tool should provide a way to add this information
3. Run tool to send takedown email
    Repos are tagged as “waiting”
4. Run tool again to examine which repos have been taken down
    If a repo was successfully taken down by its owner, it should be tagged as “done”
5. Run tool again to send second wave of emails
    Send email to owners who still haven’t taken down their repo
    Repos are tagged as “waiting #2”
"""