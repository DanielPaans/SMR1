MODULE Module1

    !Robottargets:
    CONST robtarget Home:=[[1600,-800,1600],[0,0,1,0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Sleeve_side_general:=[[-120,900,-10],[1,0,0,0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Sleeve_above_general:=[[-120,350,-30],[1,0,0,0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget mandrell_500mm:=[[0,0,-500],[1,0,0,0],[-1,1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget mandrell_90deg_500mm:=[[0,-200,-500],[0.500000052,-0.499999749,-0.500000114,0.500000085],[-1,-2,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget mandrell_90deg_275mm:=[[0,-200,-275],[0.500000052,-0.499999749,-0.500000114,0.500000085],[-1,-2,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget mandrell_90deg_min50mm:=[[0,-200,50],[0.500000052,-0.499999749,-0.500000114,0.500000085],[-1,-2,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget mandrell_30mm:=[[0,0,-30],[1,0,0,0],[-1,1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget mandrell_min50mm:=[[0,0,50],[1,0,0,0],[-1,1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget mandrell_30mm_turn:=[[0,400,-30],[1,0,0,0],[-1,1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget mandrell_sleeve_turn:=[[210.991276954,1147.758336403,266.207446028],[1,0,0,0],[-1,1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Above_Laser_turn:=[[83,0,148],[0,0.25882,0.96593,0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    VAR robtarget Sleeve_side_Specific:=[[600,350, 30],[1,0,0,0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget Sleeve_side_Specific2:=[[600,900,200],[1,0,0,0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget Sleeve_above_Specific:=[[900,350, -30],[1,0,0,0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget Sleeve_in_Specific:=[[900,350,290],[1,0,0,0],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget Sleeve_in_Specific_20:=[[900,350,20],[1,0,0,0],[-1,-1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget mandrell_90deg_275mm_Specific:=[[0,-140,-275],[0.500000052,-0.499999749,-0.500000114,0.500000085],[-1,-2,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget mandrell_90deg_min50mm_Specific:=[[0,-140,50],[0.500000052,-0.499999749,-0.500000114,0.500000085],[-1,-2,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget Above_Laser:=[[83,0,148],[0,0,1,0],[-1,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR robtarget mandrell_30mm_Var:=[[0,0,-30],[1,0,0,0],[-1,1,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    !speeddata
    VAR speeddata vrotate := [ 10, 30, 5000, 1000 ];
    VAR speeddata vrotate2 := [ 10, 6, 5000, 1000 ];
    
    !Data transfer:
    CONST string robot_ip := "10.24.8.2";
    CONST num robot_port := 1025;
    
    VAR socketdev server_socket;
    VAR socketdev client_socket;
    VAR string client_ip;
    VAR string receive_string;

    VAR num posX;  
    VAR num posY;
    VAR num posDirection;
    VAR num x;
    VAR num y;
    VAR string direction;
    VAR bool okay;
    VAR num size;
    VAR num z;
    VAR num angle;
    VAR num angle2;
    VAR num angle3;
    VAR num angle_list;
    VAR num count;
    VAR bool slot;
    VAR bool found_slot;
    
    !other:
    VAR bool stp;
    VAR bool ret;
    
    
    
    !main code
    PROC main()
        stp := FALSE; !set stop to false so when a stop is called it can be set to true.
        ret := FALSE; !set return to false so when a return is called it can be set to true.
        
        WHILE TRUE DO
            
            MoveJ Home,v500,fine,Gripper_closed\WObj:=wobj0; !return to home before asking coordinates
            AdjustCoords;   !function to update all the sleeve coordinates
            IF stp = TRUE THEN !Stp is called the program skips to the end and stops.
                GOTO label1;
            ENDIF
            
            !pickup the sleeve and position it above the laser:
            Begin;
            Pickup_Sleeve_1;
            gripper_out; !Turn actuators on here
            Pickup_Sleeve_2;
            Put_Sleeve_Laser;
            
            Adjust_Coords_Slot_And_Diameter; !function to see where the slot is and what the diameter is and to update coordinates
            IF ret = TRUE THEN !Return is called the program skips to putting the sleeve back onto the cart.
                ret := FALSE; !set return to false so when a return is called it can be set to true.
                GOTO label2;
            ENDIF
            
            !Put sleeve onto mandrell and complete proces with putting sleeve back into cart:
            Put_Sleeve_Mandrell;
            gripper_in; !Turn actuators off here
            Move_out_of_sleeve_mandrell;
            Push_Sleeve_Specific;
            Move_away_mandrell;
            !Wait for FAMM to finish
            WaitTime (5);
            Move_back_to_mandrell;
            Pull_Sleeve_Specific;
            Move_in_to_sleeve_mandrell;
            gripper_out; !Turn actuators on here
            Remove_Sleeve_Mandrell;
            label2: !goto to put the sleeve back if there is a problem with the laser data.
            Return_Sleeve_1;
            gripper_in; !Turn actuators off here
            Return_Sleeve_2;
            End;
            IF stp = TRUE THEN !Stp is called the program skips to the end and stops.
                GOTO label1;
            ENDIF
        
        ENDWHILE
        
        label1: !goto to end the program and connection with raspberry
        SocketClose server_socket;
        SocketClose client_socket;
    ENDPROC
    

    
    
    !data transfer:
    PROC server_messaging(string data_type)
    ! Create, bind, listen and accept of sockets in error handlers
    SocketSend client_socket \Str := data_type;
    SocketReceive client_socket \Str := receive_string \Time := 10; !10 seconds of waiting
    TPWrite receive_string;
    ! Wait for acknowlegde from client 
    ERROR
    IF ERRNO=ERR_SOCK_TIMEOUT THEN
    ResetRetryCount;
    RETRY;
    ELSEIF ERRNO=Err_SOCK_CLOSED THEN
    ResetRetryCount;
    server_recover;
    RETRY;
    ELSE
    ! No error recovery handling
    ENDIF
    ENDPROC
    
    PROC server_recover()
    SocketClose server_socket;
    SocketClose client_socket;
    SocketCreate server_socket;
    SocketBind server_socket, robot_ip, robot_port;
    SocketListen server_socket;
    SocketAccept server_socket,
    client_socket \ClientAddress:=client_ip \Time := 10; !10 seconds of waiting
    ERROR
    IF ERRNO=ERR_SOCK_TIMEOUT THEN
    ResetRetryCount;
    RETRY;
    ELSEIF ERRNO=ERR_SOCK_CLOSED THEN
    RETURN;
    ELSE
    ! No error recovery handling
    ENDIF
    ENDPROC
    
  
    !Adjust dynamic coordinates for sleeves:
    PROC AdjustCoords()
        !requesting coordinates in x;y;direction;
        server_messaging("coords"); !send a string Coords to request for coordinates of the sleeve.
        IF receive_string = "none" THEN !if no coordinates are available and the program needs to stop, none gets send.
            stp := TRUE;
            RETURN;
        ENDIF
        posX := StrFind(receive_string,1,";");
        posY := StrFind(receive_string,posX+1,";");
        posDirection := StrFind(receive_string,posY+1,";");
        okay := StrToVal(Strpart(receive_string, 1, posX-1), x);
        okay := StrToVal(Strpart(receive_string, posX+1, posY-posX-1), y);
        direction := Strpart(receive_string, posY+1, posDirection-posY-1);
        !values are now saved in x,y,direction in their corresponding values
        
        !check to see if the coordinates are within the working range
        IF NOT (x >= 70 AND x <= 970) THEN
            stp := TRUE;
            TPWrite "X coordinate is not within range, stopping program";
            RETURN;
        ENDIF
        IF NOT (y >= -20 AND y <= 650) THEN
            stp := TRUE;
            TPWrite "Y coordinate is not within range, stopping program";
            RETURN;
        ENDIF
        
        !insert x and y values in coordinates
        Sleeve_above_Specific.trans.x := x;
        Sleeve_above_Specific.trans.y := y;
        Sleeve_in_Specific.trans.x := x;
        Sleeve_in_Specific.trans.y := y;
        Sleeve_in_Specific_20.trans.x := x;
        Sleeve_in_Specific_20.trans.y := y;
        
        !depending on the direction the 250 is added or substracted to the x value
        Sleeve_side_Specific.trans.x := x;
        Sleeve_side_Specific.trans.y := y;
        Sleeve_side_Specific2.trans.x := x;
        IF direction = "left" THEN
            Sleeve_side_Specific := Offs (Sleeve_side_Specific, 250, 0, 0);
            Sleeve_side_Specific2 := Offs (Sleeve_side_Specific2, 250, 0, 0);
        ELSEIF direction = "right" THEN
            Sleeve_side_Specific := Offs (Sleeve_side_Specific, -250, 0, 0);
            Sleeve_side_Specific2 := Offs (Sleeve_side_Specific2, -250, 0, 0);
        ELSE
            stp := TRUE;
            TPWrite "no side given to move to at the sleeve area, stopping program";
            RETURN;
        ENDIF
        
    ENDPROC
    
    
    !Adjust coordinates for V and rotation in combination with laser sensor:
    PROC Adjust_Coords_Slot_And_Diameter()
 
        !checking the size and setting the digital out correctly
        angle2 := -180; !the angle of the sleeve should have angle -180 in the initial position.
        Above_Laser.rot :=  OrientZYX(angle2, 0, 180); !changes the coordinate angle
        Above_Laser.robconf.cf6 :=  -1; !changes the config to default
        MoveJ Above_Laser,vrotate,fine,Gripper_Sleeve\WObj:=Laser;
        
        server_messaging("size"); !send a string Size to request for size of the sleeve.         
        WHILE receive_string = "0" DO !While loop to keep looping until a size is determined
            
            angle2 := angle2 + 10;
            Above_Laser.rot :=  OrientZYX(angle2, 0, 180); !changes the coordinate angle2
            !logic to get the configuration correct:
            IF angle2 >= -180 AND angle2 < -116 THEN
                Above_Laser.robconf.cf6 :=  -1;
            ELSEIF angle2 >= -116 AND angle2 < -26 THEN
                Above_Laser.robconf.cf6 :=  -2;
            ELSEIF angle2 >= -26 AND angle2 < 0 THEN
                Above_Laser.robconf.cf6 :=  -3;
            ELSEIF angle2 >= 0 AND angle2 < 64 THEN
                Above_Laser.robconf.cf6 :=  1;
            ELSEIF angle2 >= 64 AND angle2 < 154 THEN
                Above_Laser.robconf.cf6 :=  0;
            ELSEIF angle2 >= 154 AND angle2 < 180 THEN
                Above_Laser.robconf.cf6 :=  -1;
            ENDIF
            MoveJ Above_Laser,vrotate,fine,Gripper_Sleeve\WObj:=Laser;
            server_messaging("size"); !send a string Size to request for size of the sleeve. 
            
        ENDWHILE
        IF receive_string = "none" THEN !if no coordinates are available and the program needs to stop, none gets send.
            ret := TRUE;
            stp := TRUE;
            RETURN;
        ENDIF
        okay := StrToVal(receive_string,size); 
        !size is now stored in size in mm
        
        !check which sleeve it is and adjust the z value accordingly.
        IF size >= 1 and size <= 5 THEN !490 repeat
            z := -78;
            TPWrite "490 repeat detected";
        ELSEIF size >= 6 and size <= 10 THEN !520 repeat
            z := -71;
            TPWrite "520 repeat detected";
        ELSEIF size >= 24 and size <= 30 THEN !640 repeat
            z := -96;
            TPWrite "640 repeat detected";
        ELSE
            Ret := TRUE; !if a bad value is given it will put back the sleeve on the cart.
            TPWrite "Error in sleeve diameter detection, returning sleeve";
            RETURN;
        ENDIF
        
        !insert z values in coordinates y value
        mandrell_90deg_275mm_Specific.trans.y := z;
        mandrell_90deg_min50mm_Specific.trans.y := z;       

        
        !Checking where the slot is and transfering that coordiante to the mandrell coordinate:
        angle := -180; !the angle of the sleeve should have angle -180 in the initial position.
        Above_Laser.rot :=  OrientZYX(angle, 0, 180); !changes the coordinate angle
        Above_Laser.robconf.cf6 :=  -1; !changes the config to default
        MoveJ Above_Laser,vrotate,fine,Gripper_Sleeve\WObj:=Laser;
        
        slot := TestDI(DITrigger0);
        WHILE slot = FALSE DO !digitalread 1 = False
            angle := angle + 1; !adds 1 degrees to the angle every time
                        
            IF angle = 180 THEN !To stop the loop at the maximum if slot is not found
                ret := TRUE;
                TPWrite "Slot has not been found, returning sleeve";
                RETURN;
            ENDIF
            
            Above_Laser.rot :=  OrientZYX(angle, 0, 180); !changes the coordinate angle
            !logic to get the configuration correct:
            IF angle >= -180 AND angle < -116 THEN
                Above_Laser.robconf.cf6 :=  -1;
            ELSEIF angle >= -116 AND angle < -26 THEN
                Above_Laser.robconf.cf6 :=  -2;
            ELSEIF angle >= -26 AND angle < 0 THEN
                Above_Laser.robconf.cf6 :=  -3;
            ELSEIF angle >= 0 AND angle < 64 THEN
                Above_Laser.robconf.cf6 :=  1;
            ELSEIF angle >= 64 AND angle < 154 THEN
                Above_Laser.robconf.cf6 :=  0;
            ELSEIF angle >= 154 AND angle < 180 THEN
                Above_Laser.robconf.cf6 :=  -1;
            ENDIF
            IF angle = 0 THEN
                MoveJ Above_Laser,vrotate,z1,Gripper_Sleeve\WObj:=Laser;
                WaitTime(0.5);
            ENDIF
            MoveJ Above_Laser,vrotate2,z1,Gripper_Sleeve\WObj:=Laser;
            slot := TestDI(DITrigger0);
            
        ENDWHILE
        
        !another loop to get a more acurrate slot position
        angle3 := angle - 8;
        count := 0;
        angle_list:= 0;
        
        found_slot := FALSE;
        WHILE found_slot = FALSE DO !found slot is false
            angle3 := angle3 + 0.5; !adds 1 degrees to the angle every time
                        
            IF angle3 >= (angle + 5) THEN !To stop the loop at the maximum if slot is not found
                ret := TRUE;
                TPWrite "Slot has not been found, returning sleeve";
                RETURN;
            ENDIF
            
            Above_Laser.rot :=  OrientZYX(angle3, 0, 180); !changes the coordinate angle
            !logic to get the configuration correct:
            IF angle3 >= -180 AND angle3 < -116 THEN
                Above_Laser.robconf.cf6 :=  -1;
            ELSEIF angle3 >= -116 AND angle3 < -26 THEN
                Above_Laser.robconf.cf6 :=  -2;
            ELSEIF angle >= -26 AND angle < 0 THEN
                Above_Laser.robconf.cf6 :=  -3;
            ELSEIF angle3 >= 0 AND angle3 < 64 THEN
                Above_Laser.robconf.cf6 :=  1;
            ELSEIF angle3 >= 64 AND angle3 < 154 THEN
                Above_Laser.robconf.cf6 :=  0;
            ELSEIF angle3 >= 154 AND angle3 < 180 THEN
                Above_Laser.robconf.cf6 :=  -1;
            ENDIF
            IF angle3 = 0 THEN
                MoveJ Above_Laser,vrotate,fine,Gripper_Sleeve\WObj:=Laser;
                WaitTime(0.5);
            ENDIF
            MoveJ Above_Laser,vrotate2,fine,Gripper_Sleeve\WObj:=Laser;
            WaitTime(0.5);
            slot := TestDI(DITrigger0);
            
            IF slot = TRUE THEN
                angle_list := angle_list + angle3;
                count := count + 1;
            ELSEIF (slot = FALSE) AND count >= 3 THEN
                angle := angle_list / count;
                found_slot := TRUE;
            ENDIF
            
        ENDWHILE
        
        !change the laser coordinates back to default:
        Above_Laser.rot :=  OrientZYX(-180, 0, 180); !changes the coordinate angle back to -180
        Above_Laser.robconf.cf6 :=  -1; !changes the config back to -1
        MoveJ Above_Laser,v100,fine,Gripper_Sleeve\WObj:=Laser;
        
        !change the mandrell orientation:
        angle := ((angle * (-1)) -5.8); !make the angle inverted, so it is aligned, also substract or add to the angle.
        IF angle >= 180 THEN 
            angle := angle - 360; 
        ELSEIF angle < -180 THEN
            angle := angle + 360;
        ENDIF

        mandrell_30mm_Var.rot :=  OrientZYX(angle, 0, 0); !changes the coordinate angle for the mandrell to the right value

        
    ENDPROC
 
    
    !gripper pneumatics:
    PROC gripper_in()
        SetDO cilinder0, 0;
        WaitTime 3;
    ENDPROC
    PROC gripper_out()
        SetDO cilinder0, 1;
        WaitTime 3;        
    ENDPROC
    
    
    !paths:
    PROC Begin()
        MoveJ Home,v100,fine,Gripper_closed\WObj:=wobj0;
        MoveJ Sleeve_side_general,v600,z1,Gripper_closed\WObj:=Sleeves;
        MoveL Sleeve_above_general,v600,z1,Gripper_closed\WObj:=Sleeves;
    ENDPROC
    PROC Pickup_Sleeve_1()
        MoveL Sleeve_above_Specific,v600,fine,Gripper_closed\WObj:=Sleeves;
        Break;
        MoveL Sleeve_in_Specific_20,v10,fine,Gripper_closed\WObj:=Sleeves;
        MoveL Sleeve_in_Specific,v100,fine,Gripper_closed\WObj:=Sleeves;
        MoveL Sleeve_in_Specific,v10,fine,Gripper\WObj:=Sleeves;
    ENDPROC
    PROC Put_Sleeve_Mandrell()
        MoveL Above_Laser_turn,v200,z1,Gripper_Sleeve_Horizontal\WObj:=Laser;
        MoveJ mandrell_sleeve_turn,v200,z1,Gripper_Sleeve_Horizontal\WObj:=Mandrell;
        MoveJ mandrell_30mm_turn,v200,z1,Gripper_Sleeve_Horizontal\WObj:=Mandrell;
        MoveL mandrell_30mm,v200,fine,Gripper_Sleeve_Horizontal\WObj:=Mandrell;
        Break;
        SetDO mandrel0, 1;
        WaitTime (1);
        MoveL mandrell_min50mm,v10,fine,Gripper_Sleeve_Horizontal\WObj:=Mandrell;
        MoveL mandrell_30mm,v100,fine,Gripper\WObj:=Mandrell;
        ConfJ \Off;
        MoveJ mandrell_30mm_Var,vrotate,fine,Gripper\WObj:=Mandrell;!variable coordinate that changes the angle according to the measured angle.
        ConfJ \On;
        SetDO mandrel0, 0;
    ENDPROC
    PROC Put_Sleeve_Laser()
        MoveL Above_Laser,v200,fine,Gripper_Sleeve\WObj:=Laser;
    ENDPROC
    PROC Move_out_of_sleeve_mandrell()
        ConfJ \Off;
        MoveJ mandrell_30mm_Var,v10,fine,Gripper_closed\WObj:=Mandrell;!variable coordinate that changes the angle according to the measured angle.
        ConfJ \On;
        MoveL mandrell_30mm,v10,fine,Gripper_closed\WObj:=Mandrell;
        MoveL mandrell_500mm,v200,z1,Gripper_closed\WObj:=Mandrell;
        MoveJ mandrell_90deg_500mm,v300,z1,Gripper_closed_V\WObj:=Mandrell;
        MoveL mandrell_90deg_275mm,v200,fine,Gripper_closed_V\WObj:=Mandrell;
    ENDPROC
    PROC Push_Sleeve_Specific()
        MoveL mandrell_90deg_275mm_Specific,v20,fine,Gripper_closed_V\WObj:=Mandrell;
        SetDO mandrel0, 1;
        WaitTime (1);
        MoveL mandrell_90deg_min50mm_Specific,v50,fine,Gripper_closed_V\WObj:=Mandrell;
        SetDO mandrel0, 0;
    ENDPROC
    PROC Move_away_mandrell()
        MoveL mandrell_90deg_min50mm,v20,fine,Gripper_closed_V\WObj:=Mandrell;
        MoveL mandrell_90deg_500mm,v200,fine,Gripper_closed_V\WObj:=Mandrell;
    ENDPROC
    PROC Move_back_to_mandrell()
        MoveL mandrell_90deg_500mm,v200,fine,Gripper_closed_V\WObj:=Mandrell;
        MoveL mandrell_90deg_min50mm,v200,fine,Gripper_closed_V\WObj:=Mandrell;
    ENDPROC
    PROC Pull_Sleeve_Specific()
        MoveL mandrell_90deg_min50mm_Specific,v20,fine,Gripper_closed_V\WObj:=Mandrell;
        SetDO mandrel0, 1;
        WaitTime (1);
        MoveL mandrell_90deg_275mm_Specific,v50,fine,Gripper_closed_V\WObj:=Mandrell;
        SetDO mandrel0, 0;
    ENDPROC
    PROC Move_in_to_sleeve_mandrell()
        MoveL mandrell_90deg_275mm,v20,fine,Gripper_closed_V\WObj:=Mandrell;
        MoveL mandrell_90deg_500mm,v200,z1,Gripper_closed_V\WObj:=Mandrell;
        MoveJ mandrell_500mm,v300,z1,Gripper_closed\WObj:=Mandrell;
        MoveL mandrell_30mm,v100,fine,Gripper_closed\WObj:=Mandrell;
        MoveL mandrell_30mm,v10,fine,Gripper\WObj:=Mandrell;
    ENDPROC
    PROC Remove_Sleeve_Mandrell()
        SetDO mandrel0, 1;
        WaitTime (1);
        MoveL mandrell_30mm,v100,fine,Gripper_Sleeve_Horizontal\WObj:=Mandrell;
        SetDO mandrel0, 0;
        MoveL mandrell_30mm_turn,v200,z1,Gripper_Sleeve_Horizontal\WObj:=Mandrell;
        MoveJ mandrell_sleeve_turn,v200,z1,Gripper_Sleeve_Horizontal\WObj:=Mandrell;
        MoveJ Above_Laser_turn,v200,z1,Gripper_Sleeve_Horizontal\WObj:=Laser;
    ENDPROC
    PROC Pickup_Sleeve_2()
        MoveL Sleeve_above_Specific,v200,fine,Gripper\WObj:=Sleeves;
        MoveL Sleeve_side_Specific,v200,z1,Gripper\WObj:=Sleeves;
        MoveL Sleeve_side_Specific2,v200,z1,Gripper\WObj:=Sleeves;
    ENDPROC
    PROC Return_Sleeve_1()
        MoveL Sleeve_side_Specific2,v200,z1,Gripper\WObj:=Sleeves;
        MoveL Sleeve_side_Specific,v200,z1,Gripper\WObj:=Sleeves;
        MoveL Sleeve_above_Specific,v200,fine,Gripper\WObj:=Sleeves;
        MoveL Sleeve_in_Specific,v100,fine,Gripper\WObj:=Sleeves;
    ENDPROC
    PROC Return_Sleeve_2()
        MoveL Sleeve_in_Specific,v10,fine,Gripper_closed\WObj:=Sleeves;
        MoveL Sleeve_above_Specific,v600,fine,Gripper_closed\WObj:=Sleeves;
    ENDPROC
    PROC End()
        MoveL Sleeve_above_general,v600,z1,Gripper_closed\WObj:=Sleeves;
        MoveL Sleeve_side_general,v600,z1,Gripper_closed\WObj:=Sleeves;
        MoveJ Home,v600,fine,Gripper_closed\WObj:=wobj0;
    ENDPROC
    
    

    
    
    
ENDMODULE