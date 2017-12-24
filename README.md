## TRISIS / TRITON / HatMan Malware Repository

### Description

This repository contains original samples and decompiled sources of malware attacking commonly used in Industrial Control Systems (ICS) *Triconex* Safety Instrumented System (SIS) controllers. For more information scroll to "*Learn More*".

Each organization describing this malware in reports used a different name (TRISIS/TRITON/HatMan). For that reason, there is no one, common name for it.

 Folder *original_samples* contains original files used by the malware that could be found in the wild:

| Name       | MD5                              | Contains        | MD5                              |
| ---------- | -------------------------------- | --------------- | -------------------------------- |
| trilog.7z  | 0b4e76e84fa4d6a9716d89107626da9b | trilog.exe      | 6c39c3f4a08d3d78f2eb973a94bd7718 |
| library.7z | 76f84d3aee53b2856575c9f55a9487e7 | library.zip     | 0face841f7b2953e7c29c064d6886523 |
| imain.7z   | d173e8016e73f0f2c17b5217a31153be | imain.bin       | 437f135ba179959a580412e564d3107f |
| all.7z     | 5472e9e6d7fcb34123286878e1fecf85 | All files above | -                                |

All archives are secured with password: *infected*

Folder *decompiled_code* contains decompiled python files, originating from *trilog.exe* file and *library.zip* archive described above:

| Origin      | Result                  | Method                |
| ----------- | ----------------------- | --------------------- |
| trilog.exe  | script_test.py          | unpy2exe + uncompyle6 |
| library.zip | Files in folder library | uncompyle6            |

Folder *yara_rules* contains yara rules (that I am aware of) detecting this malware:

| File          | Author                    |
| ------------- | ------------------------- |
| mandiant.yara | @itsreallynick (Mandiant) |
| ics-cert.yara | DHS/NCCIC/ICS-CERT        |

### Why Publishing? Isn't it dangerous?

Some people in the community were raising the issue that publishing the samples and decompiled sources might be dangerous. I agreed until these were not public. I have found the included files in at least two publicly available sources, that means anyone can download it if know where to search. What is more, I believe that organizations/people who could be able to reuse it and have the capability to deploy it in a real attack have already accessed it long time ago. This repository makes it more accessible for community and academia who might work on improving defense solutions and saves some time on looking for decompilers.

### Learn more:

* Report by Dragos:

  https://dragos.com/blog/trisis/TRISIS-01.pdf

* Report by Mandiant (FireEye):

  https://www.fireeye.com/blog/threat-research/2017/12/attackers-deploy-new-ics-attack-framework-triton.html

* Report by ICS-CERT (NCCIC):

  https://ics-cert.us-cert.gov/sites/default/files/documents/MAR-17-352-01%20HatMan%E2%80%94Safety%20System%20Targeted%20Malware_S508C.pdf

* Webinar by Dragos:

  https://vimeo.com/248057640



**Any updates to the repository are warmly welcome**