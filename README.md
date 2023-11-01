Sure, here's an improved version of your README file:

# SMR1 - Sleeve Mounting Robot

**SMR1** is a project developed for Flexilogic, aimed at employing a robot to retrieve Tetrapak sleeves from a cart and store them in the Fully Automatic Mounting Machine (FAMM 3.0) for mounting printing plates on the sleeve.

## Raspberry Setup

This code is designed to run on a Raspberry Pi. To set up your Raspberry Pi for this project, follow these steps:

1. **Hardware Setup:**
   - Connect a USB camera to the lower USB port of the Raspberry Pi.
   - Connect a Baumer laser sensor to the upper USB port of the Raspberry Pi.
   - Ensure the Raspberry Pi is connected to a Local Area Network (LAN) via a UTP cable to facilitate communication with the robot.

![Raspberry Pi Setup](https://github.com/DanielPaans/SMR1/assets/62547903/45953502-6eb6-4a91-8348-f84fd5e4c96c)

## Frontend Setup

Before running the application, ensure you have `npm` installed on your system. If not, you can install it with the following command:

```bash
sudo apt-get install npm
```

To set up the frontend, navigate to the "frontend" directory using the command:

```bash
cd frontend/
```

Then, build the styling with the following command:

```bash
npm run build:css
```

## Running the Application

To run the SMR1 application, execute the following command on your Raspberry Pi:

```bash
python3 sleeve_picker.py
```

This will start the robot's sleeve retrieval and mounting process.

Please feel free to add any additional details or information specific to your project as needed.
