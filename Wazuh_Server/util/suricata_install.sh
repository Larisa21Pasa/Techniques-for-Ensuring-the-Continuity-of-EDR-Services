#!/bin/bash

# Script to update suricata.yaml for dynamic HOME_NET, enable Community Flow ID, and create a custom rule

# Update and install Suricata (optional, remove if already installed)
 sudo apt-get update
 sudo apt-get install software-properties-common
 sudo add-apt-repository ppa:oisf/suricata-stable
 sudo apt-get update
 sudo apt-get install suricata -y

# Update Suricata rules (optional, remove if already updated)
 sudo suricata-update

# Define the dynamic network variable
HOME_NET_DYNAMIC=$(ip a | grep eth0 | awk '{print $2}' | cut -d':' -f2)
 REPLACEMENT_TEXT="\"[ $HOME_NET_DYNAMIC]\""

# Create custom rules directory (if not exists)
sudo mkdir -p /etc/suricata/rules

# Create custom.rules file with basic ping rule
sudo cat <<EOF > /etc/suricata/rules/custom.rules
alert icmp any any -> any any (msg:"ICMP Ping"; sid:10000001; rev:1;)
EOF
# Configure Suricata

# sudo awk -v replacement="$REPLACEMENT_TEXT" '$1 == "HOME_NET:" {$2 = replacement} 1' /etc/suricata/suricata.yaml > /tmp/suricata_modified.yaml && sudo mv /tmp/suricata_modified.yaml /etc/suricata/suricata.yaml

sudo awk -v replacement="$REPLACEMENT_TEXT" '{
    if ($1 == "HOME_NET:") {
        $2 = replacement;  # Facem înlocuirea dorită
        sub(/^/,"    ");  # Adăugăm două tab-uri înainte de linia înlocuită
    }
    print;
}' /etc/suricata/suricata.yaml > /tmp/suricata_modified.yaml && sudo mv /tmp/suricata_modified.yaml /etc/suricata/suricata.yaml





# Enable Community Flow ID
if grep -q '^community-id:' /etc/suricata/suricata.yaml; then
  # If line exists, replace value with sed
  sudo sed -i "s|community-id: false|community-id: true|" /etc/suricata/suricata.yaml
else
  # If line doesn't exist, add it with sed
  echo "community-id: true" >> /etc/suricata/suricata.yaml
fi

# Define path to custom rules file
CUSTOM_RULES_PATH="/etc/suricata/rules/custom.rules"

# Update Suricata configuration file to include custom rules
if grep -q '^rule-files:' /etc/suricata/suricata.yaml; then
  # If rule-files section exists, add custom rule path to it
  sudo sed -i "/^rule-files:/a \ \ \ - $CUSTOM_RULES_PATH" /etc/suricata/suricata.yaml
else
  # If rule-files section doesn't exist, create it and add custom rule path
  sudo sed -i "/^default-rule-path:/a rule-files:\n  - $CUSTOM_RULES_PATH" /etc/suricata/suricata.yaml
fi



sudo suricata -T -c /etc/suricata/suricata.yaml -v

echo "Check status suricata"

sudo systemctl status suricata.service

echo "Start suricata....."
sudo systemctl start suricata.service



echo "Check again status suricata......."
sudo systemctl status suricata.service

echo "HOME_NET configuration, Community Flow ID enabled, and custom ping rule added!"


