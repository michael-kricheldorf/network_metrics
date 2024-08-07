# what needs to happen:

# ------ ARGUMENTS -------
# take -p as argument to install ping
# take -r as argument to install rnode / reinstall tncattach
# take -m as argument to install modem_USB730L software

# ------ ALL -------
# edit systemd unit files to current working directory
# clear databases

# ------ FOR PING SETUP ------
# take gateway name as argument and copy/paste that file as ./ping_config.json
# also use gateway name to locate appropriate ping timer unit file

# make custom ping and modem times for each gateway so that they don't
# interfere, and so that Norvel and Mia's are synced to after Mia
# pushes data to GitHub

# install pip3 install ./ping/pythonping-1.1.4-py3-none-any.whl

# ------ 