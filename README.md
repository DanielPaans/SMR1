# SMR1
This is project for Flexilogic that plans to employ a robot to retrieve Tetrapak sleeves from a cart and store them in the Fully Automatic Mounting Machine (FAMM 3.0) for mounting printingplates on a sleeve.

## Setup raspberry
This code is meant to setup on a raspberry pi. The raspberry has two usb ports connected, the below one should be connected to a usb camera and the top one another should be connected to a Baumer laser sensor. Also the raspberry pi should be connected with a UTP cable to the LAN, to be able to communicate to the robot.
![IMG_20231101_122409080](https://github.com/DanielPaans/SMR1/assets/62547903/45953502-6eb6-4a91-8348-f84fd5e4c96c)

## Setup frontend
First you should make sure to hava `npm` installed.
```sudo apt-get install npm```
For the frontend you should navigate to the frontend directory
```cd frontend/```
After that you can build the styling with:
```npm run build:css```

## Run application
```python3 sleeve_picker.py```
