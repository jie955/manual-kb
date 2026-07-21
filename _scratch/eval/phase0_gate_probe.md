# Phase 0.3 · E2E Gate Probe

**Date**: 2026-07-08 · **generate**=True · **model**=`_scratch/modelscope/BAAI/bge-m3`

**Plan**: [Implementation Plan §4.3](./cs_en_implementation_plan.md) · **JSON**: [`cs_e2e_gate_results.json`](./cs_e2e_gate_results.json)

## Summary

| Metric | Value |
| --- | --- |
| Gate cases | 9 |
| Top1 hit (scorable) | 5/6 |
| context_zh_leak | 0 |
| Generated replies | 9/9 |

## Cases

### `cs_0023` · 0023-ad5s-left-gate-auto-close-cycle-erratic

| Field | Value |
| --- | --- |
| Top1 | `qa_040` [MISS] |
| Library | `ad5s` (keyword) |
| Expected groups | `qa_015, qa_016, qa_020` |
| Top3 | `qa_040, qa_040, qa_040` |
| ZH leak | ✅ |
| Style | `F6_auto_close_rebound` (keywords:1) |
| Reply len | 2263 |

#### System Reply

```text
Dear Customer,

Thank you for contacting TOPENS. This is Joyce from TOPENS Customer Service Team. It will be a pleasure to assist you today.

I'm sorry to hear about the trouble you're experiencing with the AD5S gate opener—having the left gate stop short, close early, and cycle on its own certainly sounds frustrating. Don't worry, we will do our best to help you get this sorted out. All TOPENS products are backed by a 12-month warranty.

Checked with our engineer, please help us do some tests to find out the problem, so that we can provide corresponding help.

1. Please double check all the brackets and hardware of the arm (including the screw of the limit switch) are secured, since looseness of the brackets or limit switch may cause this issue.

2. Power off the system, turn the FORCE potentiometer clockwise to increase the stall force to max. Then turn on the power and operate the gate opener to run for a complete opening and closing cycle. See whether the gate will open and close normally in the next opening and closing cycle.

3. If the issue is still unresolved, please use the release key to disengage the clutches of both arms, and check whether the gate itself can be manually opened and closed freely 3.3 feet (one meter) away from the gate hinge. If not, please let me know the weight and length of your gate, and double check the gate to make sure it can run freely by hand.

4. If the above step is fine, please take down the arm from the gate and hold its front mount with your hand. Then press the remote to see if the arm can extend and retract properly each time.

Please let me know the results of each step one by one so that we can better determine the problem. A video showing what the gate is doing would be greatly appreciated. If sending the video as an attachment isn't successful, you can share it through Dropbox, iCloud, or Google Drive. Could you also kindly provide your order number and shipping address with zip code and phone number? This way, if a replacement part is needed, we can assist you more quickly.

Thank you once again for being a valued customer! Your complete satisfaction is what we strive for. We at TOPENS are always standing by and ready to help.

Best regards,
Joyce
TOPENS Customer Service Team
```

### `cs_0024` · 0024-minnesota-solar-at6132s-vs-ad5s-presales

| Field | Value |
| --- | --- |
| Top1 | `qa_040` [n/a] |
| Library | `ad5s` (keyword) |
| Expected groups | `—` |
| Top3 | `qa_040, qa_015, qa_015` |
| ZH leak | ✅ |
| Style | `F7_presales` (scenario:presales) |
| Reply len | 2379 |

#### System Reply

```text
Dear Customer,

Thank you for contacting TOPENS. This is Lori from TOPENS Customer Service Team. It will be a pleasure to assist you today.

I am so sorry to hear your dog got out on the road. Let’s make sure we get your gate set up safely and reliably.

Both the AT6132S and AD5S are solid choices. For your gates—under 100 lb each, with wheels, and running on solar in Minnesota—the AD5S is our best recommendation. It is lighter duty, more energy efficient, and the wheels will help it run easily. The AD5S can also be set to auto-close after someone drives through.

To answer your questions one by one:
1.  AD5S. It matches your lightweight gates and minimizes power drain, which is important for solar in a cold winter climate like Minnesota.
2.  Yes. The control board supports an auto-close function. You can set it with the on-board potentiometer.
3.  Our compatible weatherproof keypad is the TOPENS TKP1 Universal Wireless Keypad.
4.  The main thing to keep in mind is winter. The wheels must remain free of snow and ice buildup. The solar panel will get less sun in winter, so you may need to supplement with a trickle charger during heavy snow weeks. Otherwise, your setup looks great.
5.  Only one arm needs to be the "master" with the control box and power. The second "slave" arm receives its power directly through an extension cable from the master control box. So power goes to both arms from that one control box.
6.  Absolutely. Just make sure the wheels move smoothly and that the gate weight, as pulled by the arms, stays under the rated limit.
7.  Very easy. Each arm has a release key. You simply insert the key, disengage the clutch, and you can push the gates open or closed by hand instantly.
8.  You can purchase wherever is most convenient for you. Buying on Amazon is perfectly fine, and if you buy direct from our website (topens.com) we can sometimes offer web-exclusive support. Either way, all TOPENS products are backed by a 12-month warranty and you get our lifetime technical support.

I’d recommend also checking out the installation video and manual for the AD5S here:
Manual: https://topens.com/wp-content/uploads/2024/03/AD5S-user-manual-20240312.pdf
Video: https://youtu.be/FsRg18Cozlc

Feel free to contact us if you have any more questions. We are always standing by and ready to help.

Best regards,
Lori
TOPENS Customer Service Team
```

### `cs_0025` · 0025-tc148-stopped-warranty-replacement-composite

| Field | Value |
| --- | --- |
| Top1 | `qa_001` [OK] |
| Library | `tc148` (keyword) |
| Expected groups | `qa_001, qa_002` |
| Top3 | `qa_001, qa_002` |
| ZH leak | ✅ |
| Style | `F8_warranty_rma` (scenario:warranty_composite) |
| Reply len | 2188 |

#### System Reply

```text
Dear Customer,

Thank you for contacting TOPENS. This is Joyce from TOPENS Customer Service Team. It will be a pleasure to assist you today.

I am sorry to hear that your TC148 gate opener has stopped working. I understand how frustrating this can be, and do not worry, we will do our best to help you. All TOPENS products are backed by a 12-month warranty.

Checked with our engineer, please help us do some tests to find out the problem, so that we can provide corresponding help.

1. Disconnect the extension cable connecting the TC148 wall switch to the control board, and use a short cable instead to test whether the gate opener works properly. If it does, please confirm the distance between the TC148 switch and the control board.

2. Disconnect all wired accessories from the control board except the power supply and the arm. Then, momentarily short the push button terminals (4# and 5#) on the control board with an instant touch only, plugging in and pulling out immediately, to see if the opener responds. Please watch this video for guidance: https://drive.google.com/file/d/1VdDhyHZxmpQE5pG7BYHOJi5GYb7iZHFS/view?usp=sharing

3. If the issue disappears after removing other accessories, please check for interference from other devices connected to the push-button terminals. Using shielded wire can often help. Here is a guide for connecting multiple accessories: https://topens.com/blogs/blog-posts/how-to-connect-multiple-accessories-to-a-shared-terminal-on-a-topens-gate-opener-control-board

4. You can also try grounding the COM terminal to earth. Connect a wire from the 5# COM port on the control board to a ground screw to try to resolve potential interference with the TC148 button.

5. Please confirm the wire distance and gauge: we recommend using well-shielded 2C×22 AWG cable, and keeping the length under 15 meters when possible.

Please let me know the result one by one. If possible, kindly provide a video or clear photos of the control board connections so I can check them. Also, could you please reply with your shipping address including the zip code and phone number, in case a replacement is needed?

Best regards,
Joyce
TOPENS Customer Service Team
```

### `cs_0026` · 0026-a3a5a8-board-replaced-actuator-no-response

| Field | Value |
| --- | --- |
| Top1 | `qa_001` [OK] |
| Library | `a3s` (fan_out) |
| Expected groups | `qa_001, qa_033` |
| Top3 | `qa_001, qa_010, qa_033` |
| ZH leak | ✅ |
| Style | `F2_tc148_wired` (group_hint:qa_001) |
| Reply len | 2023 |

#### System Reply

```text
Dear Customer,

Thank you for contacting TOPENS. This is Joyce from TOPENS Customer Service Team. It will be a pleasure to assist you today.

I apologize for any inconvenience this may have caused, but do not worry, we will do our best to help you. All TOPENS products are backed by a 12-month warranty.

Checked with our engineer, please help us do some tests to find out the problem, so that we can provide corresponding help.

1. Please measure the voltage of the +BAT- terminals (11# and 12#) on the control board to see whether it is above 22V.

2. If the voltage is above 22V, please check whether the power led on the control board is ON (blinks twice per second). If it is off, check the fuse whether it was burnt out and replace the fuse if necessary. There is a backup fuse packed within the user manual pack. The fuse type is ∅5*20mm 5A 250VAC fast blow glass fuse.

3. If the voltage is below 22V, please check whether the output voltage of the adapter is 36VDC. If so, disconnect the batteries from the control board and measure the output voltage of the batteries to see whether it is above DC 22V. If the voltage of the batteries is also below 22V, please keep the batteries charged fully to try it again.

4. If it still cannot work, please check the batteries. Kindly note that a 24V 12Ah battery (or 2pcs 12V batteries connected in series may function as 24V) is required to power the gate opener. Marine or Automotive type battery is compatible.

Please let me know the result one by one. Also, kindly provide a clear photo of the control board showing the wiring connections and the LED status, and a short video of the clicking sound when the remote is pressed.

Could you please also reply with your specific shipping address with zip code and confirm a phone number available for further assistance?

Thank you again for being a valued customer! Your complete satisfaction is what we strive for. We at TOPENS are always standing by and ready to help.

Best regards,
Joyce
TOPENS Customer Service Team
```

### `cs_0027` · 0027-remote-multiple-press-no-model-generic

| Field | Value |
| --- | --- |
| Top1 | `qa_010` [OK] |
| Library | `a3s` (keyword) |
| Expected groups | `qa_010` |
| Top3 | `qa_010, qa_010, qa_010` |
| ZH leak | ✅ |
| Style | `F1_no_response` (group_hint:qa_010) |
| Reply len | 3260 |

#### System Reply

```text
Dear Customer,

Thank you for contacting TOPENS. This is Lori from TOPENS Customer Service Team. It will be a pleasure to assist you today.

I apologize for the inconvenience this intermittent issue has caused. All TOPENS products are backed by a 12-month warranty, so do not worry, we will do our best to help you.

Checked with our engineer, please help us do some tests to find out the problem, so that we can provide corresponding help.

1. Check if the blue light on the remote lights up when a button is pressed. If not, replace the two CR2025 batteries and try again. Next, erase the remote codes and reprogram the remote following the instructions in the user manual. Then test whether the remote operates the gate opener.
2. Try moving the remote closer to the gate opener. If that helps, adjust the antenna on the control board—experiment with its position, angle, and direction to improve the signal.
3. Use a jumper wire to momentarily short the push button terminals on the control board (briefly touch and remove the wire), and observe whether the gate opener responds. Repeat the test several times to check if it triggers reliably each time. If so, the gate opener system should be fine, please do step 5. If the gate opener cannot respond correctly, please proceed to step 4.
4. Disengage the clutch and manually check whether the gate moves smoothly. If not so smooth, please check the gate, installation and lubricate the arm if necessary. Then keep the clutch disengaged and press the remote—observe whether the gate opener responds each time. If so, the motor and control board should be fine, the issue should be with extra mechanical resistance. Please double check the gate, installation and lubricate the arm if necessary to eliminate the resistance. If the motor still cannot respond properly, the control board or the motor might be defective. You can test the motor referring to the following step. Disconnect the RED & BLACK wires of the arm from the control board and directly connect the wires to the LOAD output terminal of the DC 24V power source directly, the motor should run (please listen to the motor sounds). Then exchange polarity of the wires, the arm should run in the opposite direction. If the motor run properly towards two directions, then the motor is good and control board should be defective.
5. Observe the surrounding environment for any potential sources of signal interference, such as nearby high-voltage power lines, large transformers, metal fences, telecom base stations, or radio transmission towers.

Please let me know the result one by one.

Videos showing the problem and pictures of the whole control board are much appreciated for further judgement. You can directly send the video to my E-mail via the attachment. If the sending is not successful, please share the photo or video link through dropbox, icloud or google drive. Thanks for your understanding and cooperation.

And also please reply your specific SHIPPING ADDRESS with zip code and confirm PHONE # available for further assistance.

Thank you again for being a valued customer! Your complete satisfaction is what we strive for. We at TOPENS are always standing by and ready to help.

Best regards,
Lori
TOPENS Customer Service Team
```

### `cs_0013` · 0013-a3s-stops-before-fully-open

| Field | Value |
| --- | --- |
| Top1 | `qa_022` [OK] |
| Library | `a3s` (keyword) |
| Expected groups | `qa_022` |
| Top3 | `qa_022, qa_022, qa_022` |
| ZH leak | ✅ |
| Style | `F4_limit_travel` (group_hint:qa_022) |
| Reply len | 2391 |

#### System Reply

```text
Dear Customer,

Thank you for contacting TOPENS. This is Joyce from TOPENS Customer Service Team. It will be a pleasure to assist you today.

I apologize for the inconvenience this gate opening issue has caused, but do not worry, we will do our best to help you. All TOPENS products are backed by a 12-month warranty.

Checked with our engineer, please help us do some tests to find out the problem, so that we can provide corresponding help.

1. Please detect the voltage of the +BAT- terminals (11# and 12#) on the control board while pressing the remote to see whether the voltage stays at almost 24V (above 22V). If the voltage drops too much, the problem may be with the power source. If the voltage is fine, please proceed to the following tests.

2. Please power off the system first (disconnect the power source from the +BAT- terminals). Turn the FORCE potentiometer all the way clockwise to increase the stall force, and turn the SOFT STOP potentiometer all the way counter-clockwise to decrease the soft stop period. Then turn on the power and operate the gate opener through a complete opening and closing cycle. See whether the gate opens and closes all the way on the next cycle.

3. If the problem still persists, push against the gate (in the opposite direction of its movement) while the gate is opening. Continuously add some load and see whether the gate can open all the way properly.

4. If the tests above do not help, please remove the arm from the gate and hold its front mount firmly, then press the remote to see whether the arm can extend and retract properly each time. If the arm runs normally in this test, the arm itself is fine — please let me know the weight and length of your gate, and whether the gate can be opened and closed freely about 3.3 feet (one meter) from the gate hinge.

Please let me know the result one by one. Videos showing the problem and pictures of the whole control board are appreciated for further judgement. You can directly send the video to my E-mail via the attachment. If the sending is not successful, please share the photo or video link through dropbox, icloud or google drive. Thanks for your understanding and cooperation.

Thank you again for being a valued customer! Your complete satisfaction is what we strive for. We at TOPENS are always standing by and ready to help.

Best regards,
Joyce
TOPENS Customer Service Team
```

### `cs_0008` · 0008-pw502-tc148-push-button-not-working

| Field | Value |
| --- | --- |
| Top1 | `qa_001` [OK] |
| Library | `tc148` (keyword) |
| Expected groups | `qa_001, qa_002` |
| Top3 | `qa_001, qa_002` |
| ZH leak | ✅ |
| Style | `F2_tc148_wired` (group_hint:qa_001) |
| Reply len | 2179 |

#### System Reply

```text
Dear Customer,

Thank you for contacting TOPENS. This is Joyce from TOPENS Customer Service Team. It will be a pleasure to assist you today.

I apologize for any inconvenience this may have caused, but do not worry, we will do our best to help you. All TOPENS products are backed by a 12-month warranty.

Checked with our engineer, please help us do some tests to find out the problem, so that we can provide corresponding help.

1. Disconnect the extension cable connecting TC148 to the control board and replace it with a short cable to test whether the gate opener works. If it does, please confirm the distance between your TC148 and the control board.

2. Disconnect all wired accessories from the control board except the power supply and arm. Then, momentarily short (instant touch only — plug in then pull out instantly) the push button terminals (4# and 5#) to see if the opener responds. Please refer to this video: https://drive.google.com/file/d/1VdDhyHZxmpQE5pG7BYHOJi5GYb7iZHFS/view?usp=sharing

I know you've already tried jumpering 4# and 5#. Could you please try this procedure again using an instant short? A continuous jumper may not trigger the opener, as the control board requires a momentary contact signal.

3. Please confirm if the wall switch is a genuine TOPENS TC148, as third-party switches may be incompatible.

4. Check the wire distance and gauge. We recommend using well-shielded 2C×22 AWG cable and keeping the length under 15 meters when possible.

For connecting multiple accessories to a shared terminal, this guide may be helpful: https://topens.com/blogs/blog-posts/how-to-connect-multiple-accessories-to-a-shared-terminal-on-a-topens-gate-opener-control-board

Please let me know the result one by one. Also, a short video or clear photos of the control board wiring would be very helpful for further diagnosis.

And please reply with your specific SHIPPING ADDRESS with zip code and confirm your PHONE # available for further assistance.

Thank you again for being a valued customer! Your complete satisfaction is what we strive for. We at TOPENS are always standing by and ready to help.

Best regards,
Joyce
TOPENS Customer Service Team
```

### `cs_0022` · 0022-a5132-opens-then-recloses-resolved

| Field | Value |
| --- | --- |
| Top1 | `qa_040` [n/a] |
| Library | `ad5s` (keyword) |
| Expected groups | `—` |
| Top3 | `qa_040, qa_040, qa_040` |
| ZH leak | ✅ |
| Style | `F1_no_response` (keywords:1) |
| Reply len | 2294 |

#### System Reply

```text
Dear Customer,

Thank you for contacting TOPENS. This is Heidi from TOPENS Customer Service Team. It will be a pleasure to assist you today.

I apologize for the inconvenience this gate behavior is causing, but do not worry, we will do our best to help you. All TOPENS products are backed by a 12-month warranty.

Regarding your question, yes, pull-to-open configuration does influence how the arm moves, so that's helpful to know.

Checked with our engineer, please help us do some tests to find out the problem, so that we can provide corresponding help.

1. Please double check all the brackets and hardware of the arm (including the screw of the limit switch) are secured since the looseness of the brackets or limit switch may also cause this issue.

2. Power off the system, turn the FORCE potentiometer clockwise to increase the stall force to max. Then turn on the power and operate the gate opener to run for a complete opening & closing cycle. See whether the gate will open and close normally in the next opening and closing cycle.

3. If the issue is still unresolved, please use the release key to disengage the clutches of both arms, and check whether the gate itself can be manually opened & closed freely 3.3 feet (one meter) away from the gate hinge. If not, please let me know the weight and length of your gate and double check the gate to make sure the gate can run freely by hand.

4. If the above step is fine, please take down the arm from the gate and hold its front mount with a hand. Then press the remote to see if the arm can extend and retract properly each time.

Please let me know the result one by one.

Videos showing the problem and pictures of the whole control board are much appreciated for further judgement. You can directly send the video to my E-mail via the attachment. If the sending is not successful, please share the photo or video link through dropbox, icloud or google drive. Thanks for your understanding and cooperation.

And also please reply your specific SHIPPING ADDRESS with zip code and confirm PHONE # available for further assistance.

Thank you again for being a valued customer! Your complete satisfaction is what we strive for. We at TOPENS are always standing by and ready to help.

Best regards,
Heidi
TOPENS Customer Service Team
```

### `cs_0001` · 0001-at12131s-gate-no-response

| Field | Value |
| --- | --- |
| Top1 | `qa_011` [n/a] |
| Library | `a3s` (fan_out) |
| Expected groups | `—` |
| Top3 | `qa_011, qa_011, qa_011` |
| ZH leak | ✅ |
| Style | `F1_no_response` (group_hint:qa_011) |
| Reply len | 3081 |

#### System Reply

```text
Dear Customer,

Thank you for contacting TOPENS. This is Lori from TOPENS Customer Service Team. It will be a pleasure to assist you today.

I apologize for any inconvenience this may have caused, but do not worry, we will do our best to help you.

Checked with our engineer, please help us do some tests to find out the problem, so that we can provide corresponding help.

1. Please measure the voltage of the +BAT- terminals (11# and 12#) on the control board to see whether it is above 22VDC. If the voltage is below 22VDC, please check whether the output voltage of the adapter is 36VDC. If so, disconnect the batteries from the control board and measure the output voltage of the batteries to see whether it is above 22VDC. If the battery voltage is also below 22VDC, please keep the batteries charged fully to try it again. If it still cannot work, please check the batteries. Kindly note that a 24V 12Ah battery (or 2pcs 12V batteries connected in series may function as 24V) is required to power the gate opener. Marine or Automotive type battery is compatible.

2. Disconnect all accessories from the control board first (just leave the power source and the arm). And disable the photocell function by turning the dip switch #3 off. Then erase all remotes codes from the control board and reprogram them to have a try. If it fails, please instantaneously short (plug the wire in, then pull it out immediately) the push button terminals (4# and 5#) to check whether the opener can work. You can refer to this video on how to instantaneously short the terminals: https://drive.google.com/file/d/1VdDhyHZxmpQE5pG7BYHOJi5GYb7iZHFS/view?usp=sharing

3. If there is still no luck, please release the clutches on the arm and push the gate to the middle position firstly. And engage the clutches and press the remote to see whether the gate can run towards both directions.

4. Please check the motor. Connect the red & black wires of the arm to a DC 24V power source directly, the motor should run, and then exchange the polarity of the wires, the motor should run in the opposite direction. If the motor runs in both directions, the motor itself is good. Please then disconnect the BLUE, GREEN & YELLOW wires of the arm from the control board, use two jumper wires to short the ULT, COM & DLT terminals to which the wires were connected, and then press the remote to test.

Please let me know the result one by one.

Videos showing the problem and pictures of the whole control board are much appreciated for further judgement. You can directly send the video to my E-mail via the attachment. If the sending is not successful, please share the photo or video link through dropbox, icloud or google drive. Thanks for your understanding and cooperation.

And also please reply with your specific SHIPPING ADDRESS with zip code and confirm PHONE # available for further assistance.

Thank you again for being a valued customer! Your complete satisfaction is what we strive for. We at TOPENS are always standing by and ready to help.

Best regards,
Lori
TOPENS Customer Service Team
```
