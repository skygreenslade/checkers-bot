

ticksPerRev = 8     #internal ticks per revolution (motor)
ratioToShaft = 46   #46 revs per oput rev
ratioToShaft2 = 75  #75
shaftteeth = 8      #8 teeth per shaft rotation
gear1teeth = 72     #gear 1 teeth
gear2teeth = 56     #gear 2 teeth


oput = ticksPerRev*ratioToShaft*(gear1teeth/shaftteeth)

oput2 = ticksPerRev*ratioToShaft*(gear2teeth/shaftteeth)

oput3 =  ticksPerRev*ratioToShaft2*(gear1teeth/shaftteeth)

print(oput)
print(oput2)
print(oput3)





