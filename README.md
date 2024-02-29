## About
The project was developed for the [Simulation and Modeling of Computational Systems](https://www.cs.uoi.gr/~gkappes/mye029) course @ [cse.uoi.gr](https://www.cs.uoi.gr/)

Internet service providers use a collection of server clusters to serve their customers more efficiently.
Modern server clusters are usually heterogeneous, meaning they are composed of servers with different configurations.
This is mainly due to the rapid evolution observed in server hardware over a short period and the continuous purchase and installation of new servers at different times.
An interesting research question that arises is how to make the distribution of customer tasks to servers with different processing rates more efficient so that the overall utilization of resources remains high.

In this project, one uses the method of simulation to try to answer this question. Specifically, one will learn:
1. To use the method of simulation to solve design problems.
2. To use a discrete event simulator to simulate computational systems.
3. To use statistically correct methods for analyzing the results of the simulation.

In this project, one will use the Ciw simulation library to develop a simulator for the system described. Ciw is a discrete event simulation library for open queuing networks.
The core element of Ciw is the simulation object, which consists of a network of nodes.
The simulation object consists of a network of nodes (nodes). Each node includes a distribution that describes the times between arrivals of new tasks, a distribution that describes the service times, and a number of processing units.
In this project each node consists of 1 processing unit.
