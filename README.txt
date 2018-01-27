DNS resolver - By Ben Campbell

This is a program that is built to query DNS and retrieve records about the given domain name.
I believe that the only thing that I didn't finish implementing in this program is the time it takes for each iteration.
However, it does give the total time it took to retrieve the record.

Keep in mind, when running this program, that it is very dependent upon the network that you are running it on. Depending upon the configuration of the network that it is run on, this program may not work, especially if port 53 is hijacked.

The resolver can be run by typing:

python myresolver.py commandfile.txt

where commandfile.txt is the name of the command file.
