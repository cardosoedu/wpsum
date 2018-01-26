# wpsum
A Python script that generates a file containing the checksum of every file of a Wordpress installation (excluding the wp-content directory). You can also compare this file with another list of checksums, checking the integrity of your installation.

# How to use it

There are two ways to use the script:
Automatically:
	When starting the program, you can choose to do what you want or let the script run by itself.
	When in auto mode, the script will create a JSON file based on your current Wordpress installation and compare it to the Wordpress hash files inside this repository's "sums" directory. If it can't find in the directory, an exit message will be shown.
Manual:
	You'll be asked if you want to create a JSON file with the hashes of a Wordpress directory or to compare two different files.

What I want to do to finish this project:
- Get the Wordpress version; (done)
- Create a repository with a checksum list of different Wordpress versions; (done)
- Automatically create the file contaning the checksum of the local WP and compare it with the remote JSON; (done)
