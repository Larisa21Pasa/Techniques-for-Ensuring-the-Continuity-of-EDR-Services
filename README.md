# Techniques-for-Ensuring-the-Continuity-of-EDR-Services
## IDS ROLE
Intrusion Detection and Prevention Systems (IDS/IPS) are designed to monitor data flows entering and exiting a system to detect and alert on suspicious behavior (IDS role) or to detect, alert, and directly block attacks (IPS role). A Network-based IDS (NIDS) monitors network traffic and aims to identify attacks related to System Intrusion, such as Backdoor Installation, Denial of Service, and Trojan Horse Attacks. NIDS alone cannot provide comprehensive protection for connected systems. Primarily, NIDS are focused on detecting and generating alerts and require integration into more complex solutions for effective response to alerts. Additionally, NIDS may struggle with Social Engineering attacks targeting human vulnerabilities and Zero-Day attacks due to the absence of rules for new threats.

## HIDS ROLE
Complementary to NIDS are Host-based IDS (HIDS), which, together, form part of a broader Security Information and Event Management (SIEM) solution. An Information Security and Event Management system includes HIDS functionality, meaning it can detect malicious activities at the system level, such as file modifications, and is not affected by encrypted traffic since it operates on already decrypted data on the host. Given the extensive data processed within a SIEM, automatic detection and response to attacks provide a solution aligned with current needs.

## SIEM ROLE
Thus, SIEM allows for the integration of IDS to cover a broader range of attacks. The proposed architecture in this paper is modular and is based on separate data collection flows for protected systems and response to potential alerts. These separate flows are realized through distinct server-client communication channels. The technical implementation solution is based on intrusion detection technologies, including servers and agents such as Wazuh (HIDS) and Suricata (NIDS), integrated into a coherent system for monitoring and analyzing security events.

# C2 ROLE
Management and coordination of appropriate responses to suspicious behavior detected by NIDS, correlated with HIDS, are handled through a centralized Command and Control (C2) server. Reactive C2 agents are installed on the same systems where proactive SIEM agents are configured. The SIEM agent collects alerts generated by NIDS, transfers them to the SIEM server. The C2 server processes these alerts and sends appropriate responses back to the C2 agent. The C2 agent then executes instructions to stop the suspicious behavior.

# EDR ROLE
The project is based on the principles of an Endpoint Detection and Response (EDR) system, which involves taking immediate actions against various anomalous behaviors detected on monitored systems. The intended beneficiaries of this project are Blue Team members, employing Red Team techniques such as C2.






