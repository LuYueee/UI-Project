######################################
#	CS014AL Project: Image Editor	
#	Window Prototype			        
#	Yue,Lu				                
#	10/04/2017		                
######################################

###10/04：根据原型布局，简单的框架搭建###
###10/06：Add a subpanel at the bottom of mainpanel (for crtl+z) and a panel at the top of all panels for maximize,minimize and exit###

#name of window Image Editor
wm title . "Image Editor"

###background color
###76EEC6 
###528B8B

#XO-
frame .top -background gray -height 50 -width 1700
pack .top -side top -fill both 
###这里不设置-expand###
### Maximize Minimize Exit###
button .top.b1 -text "Button1" 
pack .top.b1  -side right  -padx 10
button .top.b2 -text "Button2" 
pack .top.b2  -side right  -padx 10
###label must be at the end of mainpanel code###
label .top.label  -background gray  -text "" -width 226
pack .mainpanel.label -side top


#Menu Bar
frame .subpanel1 -background #528B8B  -height 800 
###这里不设置-expand###
pack .subpanel1 -side left -fill both 
label .subpanel1.label  -background #528B8B  -text "" -width 5
pack .subpanel1.label -side bottom
###最旁边的工具栏，按钮设置top会从上往下排###
button .subpanel1.b1 -text "Button1" 
pack .subpanel1.b1  -side top  -pady 10
button .subpanel1.b2 -text "Button2" 
pack .subpanel1.b2  -side top  -pady 10

button .subpanel1.b3 -text "Button3" 
pack .subpanel1.b3  -side top  -pady 10
button .subpanel1.b4 -text "Button4" 
pack .subpanel1.b4  -side top  -pady 10

button .subpanel1.b5 -text "Button5" 
pack .subpanel1.b5  -side top  -pady 10
button .subpanel1.b6 -text "Button6" 
pack .subpanel1.b6  -side top  -pady 10


button .subpanel1.b7 -text "Button7" 
pack .subpanel1.b7  -side top  -pady 10
button .subpanel1.b8 -text "Button8" 
pack .subpanel1.b8  -side top  -pady 10


#Tool Bar 2
frame .subpanel2 -background #76EEC6 -height 800 -width 300
pack .subpanel2 -side left -fill both -expand true
###在每个frame的最底下加入label把frame从左到右撑起来###
###width 40是最小化时工具栏的长度（后期需要调整）###
label .subpanel2.label  -background #76EEC6  -text "" -width 40
pack .subpanel2.label -side bottom

###[but] is sub frame of subpanel2###
frame .subpanel2.but1 -background #76EEC6 
pack .subpanel2.but1 -side top
button .subpanel2.but1.b1 -text "Button1"
pack .subpanel2.but1.b1  -side left  
button .subpanel2.but1.b2 -text "Button2"
pack .subpanel2.but1.b2  -side left  


frame .subpanel2.but2 -background #76EEC6 
pack .subpanel2.but2 -side top
button .subpanel2.but2.b1 -text "Button3"
pack .subpanel2.but2.b1  -side left  
button .subpanel2.but2.b2 -text "Button4"
pack .subpanel2.but2.b2  -side left  


frame .subpanel2.but3 -background #76EEC6 
pack .subpanel2.but3 -side top
button .subpanel2.but3.b1 -text "Button5"
pack .subpanel2.but3.b1  -side left  
button .subpanel2.but3.b2 -text "Button6"
pack .subpanel2.but3.b2  -side left  



#Operation Field
###作业区###
frame .mainpanel -background white -height 800 -width 1000
pack .mainpanel -side left -fill both -expand true

frame .mainpanel.bottom -background #528B8B  -width 1000
pack .mainpanel.bottom -side bottom -fill both


###Modifies by Yiran, Chen###
frame .mainpanel.bottom.ccc -background #528B8B -height 20
pack .mainpanel.bottom.ccc -side bottom 
button .mainpanel.bottom.ccc.b1 -text "Button1" 
pack .mainpanel.bottom.ccc.b1  -side right  -padx 10
button .mainpanel.bottom.ccc.b2 -text "Button2" 
pack .mainpanel.bottom.ccc.b2  -side right  -padx 10
###Modifies by Yiran, Chen###

###label must be at the end of mainpanel code###
label .mainpanel.label  -background white  -text "" -width 133
pack .mainpanel.label -side bottom


#Tool Bar 3
frame .subpanel3 -background #76EEC6 -height 800 -width 300
pack .subpanel3 -side left -fill both -expand true
label .subpanel3.label  -background #76EEC6  -text "" -width 40
pack .subpanel3.label -side bottom

