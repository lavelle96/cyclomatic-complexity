# Finding Cyclomatic Complexity of Repo using multiple nodes

This was a Cloud computing task given in the module 'Internet Applications'. I used the [Argon library](https://github.com/rubik/argon) to calculate the cyclomatic complexity of the [Argon library](https://github.com/rubik/argon) written in python

## Run
If running remotely, fill in the MASTER_IP in the config.py file, also set the commenting to remote in the format.py file.

Remember to fill in your unique git token in the config.py file.

Other parameters that you might like to test can be done so in the config file such as the repo on which you want to perform the analysis.

-Run a single worker:
python worker.py
-Run n workers:
./run_n_clients.sh n

-Run a master:
python master.py


## Method
I implemented the work stealing method of distributing work, the roles of the worker and master will be explined below

### Worker
- When a worker starts up it sends a get request to the master api looking for an id (for future identification) and the url of the repo it will be getting the cyclomatic complexity of.
- The worker then saves this id and clones the repo in question.
- It then sends a get request to the master looking for the SHA of the commit it should perform a cyclomatic complexity computation on.
- The cyclomatic complexity of that commit is calculated and sent back to the master in a post request.
- The worker looks for another SHA from the master and will continue to do so until it recieves a NULL response indicating that no more commits are left to be evaluated.

### Master
- The master first gets all the SHA's of the commits of the repository by using the github api.
- A thread is set up to keep track of how long workers have been operating on their commits (the availability status of a commit will be reset if the worker working on that commit hasnt responded in 2 seconds (can be changed in the config file).
- The master api is then set up to allow requests from workers, handing out commits to workers as the requests come in and registering the complexity of each commit as it is received from the workers.
- This is repeated until the cyclomatic complexity of each commit has been found.

## Results
I ran this system on the Argon repo, first deploying the workers and master on my machine (local trial). I then ran it using a different virtual machine for each worker/master using AWS (remote trial). Both of these trials were tried for 1-10 nodes, the results are graphed below (Number of nodes vs time taken to compute cyclomatic complexity of repo):

![alt text](https://github.com/lavelle96/cyclomatic-complexity/blob/master/graphs/Local.png)
![alt text](https://github.com/lavelle96/cyclomatic-complexity/blob/master/graphs/Remote.png)

As you can see the, the performance gets better the more nodes that were added in both cases, with the performance of the remote deployment proving significantly faster than the local deployment. However the rate of increase in performance starts to stop at 5 and 8 nodes respectively with times of 5 seconds and 21 seconds respectively. 
- For the local deployment, this is because it was deployed on a quadcore computer so couldnt have been split up anymore on the hardware. 
- For the remote deployment, it is expected that the performance would continue to improve until you had a worker on a unique machine for every single commit (165 in this case), at that point the problem could not be parallelised anymore as every worker would be computing the minimum amount of commits (1).

I was also interested to see the plot of the cyclomatic complexity of the repo over time. You can see this plotted below (commit number vs cyclomatic complexity) for the src folder and the overall repo. 

![alt text](https://github.com/lavelle96/cyclomatic-complexity/blob/master/graphs/ccvtime.png)

The results are as expected with quite a steady increase representing the growth of the repo, followed by a plateau (Perhaps the stage of 'tweaking' the code, not many lines being added).

