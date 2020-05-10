Todo list for the port of the old bot
=====================================

- : todo
+ : done

When all of the subitems of an item are done, move it to DONE.


TODO
----
- Play around the the data model that Kaggle gave us
    + Instead of using strings directly as actions/directions, etc, make
      some classes
    - Create a 2D grid internally, much easier to work with
    - Reuse Jan's code for Unit objects and cells
        - Board should contain an array of BoardCells
        - 
    - Move the remove_possibles() method to some default navigator module
    - 

- Create naive versions of Navigate and Spawn
    - Remove the logging for now
    - Naive navigate: just move in the general direction of the goal
    - Naive Spawn: I think pretty much the same as the current one, just
      pump 'em out

- Get Strategy working with the naive modules
    - Create an Objective dataclass without the logging
    - The Strategy module should distribute Objectives to units
    - Instead of calling Objective.execute(), I want to pass the Agent to pass the Objective into the Navigator. This way we can separate the Navigator and Strategy code nicely

- Try to make the timeout functionality async (!)

- Simplify some of the rules
    - Set spawning rule to be greedy
    - remove game log for now


- What does the temp_uid in Board.spawn() do?

DONE 
----
