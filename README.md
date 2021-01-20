# bookbuilder

A tool for writers using simple text editors. Write Character POVs in individual files, then combine them into a single file:

# example

## input files
luke.txt
	hoth_battle: "That armor's too strong for blasters!"
	visits_yoda: "Hey, that's my dinner!"
	fights_vader: "That's not true! That's impossible!"

han.txt
	meteor_worm: "All right, Chewie, let's get out of here!"
	cloud_city: "This deal's getting worse all the time!"

vader.txt
	emperor: "What is thy bidding, my master?"

esb_chapters.txt
	luke_hoth_battle
	han_meteor_worm
	vader_emperor
	luke_visits_yoda
	han_cloud_city
	luke_fights_vader

## command
> python bookbuilder.py esb_chapters.txt empire_strikes_back.txt luke.txt han.txt vader.txt

## output

empire_strikes_back.txt
	"That armor's too strong for blasters!"
	"All right, Chewie, let's get out of here!"
	"What is thy bidding, my master?"
	"Hey, that's my dinner!"
	"This deal's getting worse all the time!"
	"That's not true! That's impossible!"