# simulator
The simulator is a modified Batsim simulator that is packaged into a docker, so one can easily build it and run some simulations

## How to build the docker
clone this repo:<br/>
```git clone https://github.com/hpec-2021-ccu-lanl/simulator.git``` <br/>
enter directory:<br/>
```cd simulator```<br/>
build the docker and name the image "simulator": <br/>
```docker build . -t simulator```<br/>

## How to run the docker

create the docker container based off the "simulator" image and name it "batsim_docker":<br/>
```docker create --name batsim_docker -t simulator```<br/>
start the docker container: <br/>
```docker start batsim_docker```<br/>
start an interactive shell:<br/>
```docker exec -it batsim_docker /bin/bash```

