Todo list for the port of the old bot
=====================================

- : todo
+ : done

When all of the subitems of an item are done, move it to DONE.


TODO
----
- Play around the the data model that Kaggle gave us
    + Instead of using strings directly as actions/directions, etc, make
      some constants
    - Reuse Jan's code for board cells
        - Board should contain an array of BoardCells
        - A BoardCell must be able to be queried on:
            - A list of units in that cell
            - Halite in that cell
            - Average Halite (instead of gaussian blurring an array like last time,
            just take the average of yourself and your neighbours). This is essential 
            for the finding new objectives part 
            - Unique hash (position is a tuple, should be fine)
    - Move the remove_possibles() method to some default navigator module
        - In other words, find some way to track safe cells
    - Write tests

- Create naive versions of Navigate and Spawn
    + Remove the logging for now
    + Naive navigate: just move in the general direction of the goal
    + Naive Spawn: I think pretty much the same as the current one, just
      pump 'em out when possible until the end game
    - Write tests

- Get Strategy working with the naive modules
    + Instead of calling Objective.execute(), I want to pass the Agent to pass the Objective into the Navigator. 
    This way we can separate the Navigator and Strategy code nicely.
    + Create an Objective dataclass without the logging and a simplifed API
        + Method complete(board, unit), I think this should be sufficient 
        + Method next(), return the next objective (if any)
    - The Strategy module should manage Objectives assigned to units
        + Remove completed objectives
        - Find new objectves
            - High concentrations of halite weighted by distance from shipyard (mine)
            - High concentrations that are too far away from a shipyard (convert)
        - Assign objectives 
            + To closest available ships
            - To ships with most halite? This might be relevant for conversion
    
- Try to make the timeout functionality async (!)
    - Maybe the whole thing should be async? This way we can run the whole 
    thing in an async timeout and do a best effort approach to search.


? What does the temp_uid in Board.spawn() do?
    + I hope it doesnt matter, because I removed it
    - After tests are written, keep this in mind

DONE 
----
