# Phase 0.2 · Pilot Context Smoke

**Date**: 2026-07-07
**Mode**: Oracle hits · `locale=en` · post Phase 0.1 EN Context Policy

## #1 AT12131S gate no response (`cs_0001`)

**Groups**: qa_011

### Customer email (excerpt)

```
the gate does nothing when i push the button or use the key pad remote.
Product Model: TOPENS AT12131S
```

### LLM context (`locale=en`)

```
--- Reference 1 ---
Section: 完全不工作 Complete Failure
Fault title: 按遥控器/按键完全无反应 No Response At All · AT12131 Push Button Does Nothing · Gate Does Nothing When I Push the Button · Control Board Power LED Off Fuse Backup
English troubleshooting steps:
1 Please measure the voltage of the +BAT- terminals (11# and 12#) on the control board to see whether it is above 22VDC.
If so, please proceed to test 2.
If not so, please disconnect the solar panels from the TCS3 solar charge controller, and disconnect the TCS3 controller from the control board. Test the output voltage of the batteries and solar charger controller.
If the voltage of the batteries is more than 22VDC, but the voltage of LOAD terminals of the TCS3 is lower than 22VDC, the TCS3 might be defective.
If the battery voltage is below 22VDC, please charge the batteries fully with an additional charger and connect the batteries to the +BAT- terminals (11# and 12#) on the control board. And press the remote to operate the gate opener to see whether it can work. If it can work in this case, please reconnect the TCS3 back to see whether it can still work. If not, the TCS3 is defective.
On the contrary, if the opener cannot work even when connecting the full batteries to the control board directly, please move to test 2.
1 Please measure the voltage of the +BAT- terminals (11# and 12#) on the control board to see whether it is above 22VDC.
If so, please proceed to test 2.
If the voltage is below 22VDC, please check whether the output voltage of the adapter is 36VDC. If so, disconnect the batteries from the control board and measure the output voltage of the batteries to see whether it is above 22VDC. If the voltage of the batteries is also below 22VDC, please keep the batteries charged fully to try it again. If it still cannot work, please check the batteries. Kindly note that a 24V 12Ah battery (or 2pcs 12V batteries connected in series may function as 24V) is required to power the gate opener. Marine or Automotive type battery is compatible.
2 Disconnect all accessories from the control board first (just leave the power source and the arm). And disable the photocell function by turning the dip switch #3 off. Then erase all remotes codes from the control board and reprogram them to have a try. If it fails, please instantaneously short (plug the wire in, then pull it out immediately) the push button terminals (4# and 5#) to check whether the opener can work.
How to instantaneously short the “O/S/C COM” terminals:
https://drive.google.com/file/d/1VdDhyHZxmpQE5pG7BYHOJi5GYb7iZHFS/view?usp=sharing
3 If there is still no luck, please release the clutches on the arm and push the gate to the middle position firstly. And engage the clutches and press the remote to see whether the gate can run towards the both directions. If it still doesn’t help, please go on the troubleshooting below.
4 Please check the motor. Connect the red & black wires of the arm to the DC 24V power source directly, the motor should run, and then exchange the polarity of the wires, the motor should run in the opposite direction. If the motor runs in both directions, the motor itself is good. Please connect the black & red wires back to the control board and check step4.
4 Disconnect the BLUE, GREEN & YELLOW wires of the faulty arm from the control board, use two jumper wires to short the ULT, COM & DLT terminals to which the wires were connected, and then press the remote to see if the arm could extend and retract. If it could move in both directions, then the limit switch is defective. When you do this test, you could press the remote in time in case the arm extends too much.
Images:
  - image_007.png
```

**ZH leak check**: PASS

## #8 PW502 TC148 push button not working (`cs_0008`)

**Groups**: qa_002

### Customer email (excerpt)

```
Push button not working, therefore we jumpered out #4&5 at the main control panel and still nothing happened. Other than that everything works.
Product Model: PW502 · Accessories: TC148
```

### LLM context (`locale=en`)

```
--- Reference 1 ---
Section: 
Fault title: 按TC148无反应·push button短接排查 No Response · O/S/C COM Short Test
(No English troubleshooting steps in this reference.)
```

**ZH leak check**: PASS
