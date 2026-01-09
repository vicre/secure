Bitwarden JSON Encryptor – Python Virtual Environment Setup
===========================================================

This project encrypts sensitive values in a Bitwarden JSON export:
- Login passwords (items.type == 1)
- Hidden custom fields (fields.type == 1)

It outputs:
- An encrypted JSON file
- A separate decryption key file

------------------------------------------------------------
1. Prerequisites
------------------------------------------------------------

- Python 3.9 or newer
- python3-venv package (usually installed by default)

Verify Python version:

  python3 --version


------------------------------------------------------------
2. Create a Virtual Environment
------------------------------------------------------------

From the project root directory:

  cd ~/Projects/secure/python

Create the virtual environment:

  python3 -m venv .venv


------------------------------------------------------------
3. Activate the Virtual Environment
------------------------------------------------------------

Linux / macOS:

  source .venv/bin/activate

Your shell prompt should now show something like:

  (.venv) victor-reipur@DTU-5CG51911HW:~/Projects/secure$


------------------------------------------------------------
4. Install Dependencies
------------------------------------------------------------

Upgrade pip (recommended):

  python -m pip install --upgrade pip

Install required packages:

  pip install -r requirements.txt


------------------------------------------------------------
5. Run the Encryptor
------------------------------------------------------------

Example:

  python python/bw_encrypt.py bitwarden_export_example.json

This will generate:

  bitwarden_export_example_reipur_encrypted.json
  bitwarden_export_example_reipur_decryption_key.txt


------------------------------------------------------------
6. Decrypt (Optional)
------------------------------------------------------------

To decrypt an encrypted file:

  python python/bw_encrypt.py \
    bitwarden_export_example_reipur_encrypted.json \
    --decrypt \
    --keyfile bitwarden_export_example_reipur_decryption_key.txt


------------------------------------------------------------
7. Deactivate Virtual Environment
------------------------------------------------------------

When finished:

  deactivate


------------------------------------------------------------
SECURITY NOTES
------------------------------------------------------------

- The decryption key file MUST be kept secret
- Anyone with the key can decrypt all passwords
- Encrypted JSON files are NOT importable into Bitwarden
- This tool is intended for secure storage / transfer / archival

------------------------------------------------------------
Bitwarden JSON Encryptor – Python Virtual Environment Setup
===========================================================

This project encrypts sensitive values in a Bitwarden JSON export:
- Login passwords (items.type == 1)
- Hidden custom fields (fields.type == 1)

It outputs:
- An encrypted JSON file
- A separate decryption key file

------------------------------------------------------------
1. Prerequisites
------------------------------------------------------------

- Python 3.9 or newer
- python3-venv package (usually installed by default)

Verify Python version:

  python3 --version


------------------------------------------------------------
2. Create a Virtual Environment
------------------------------------------------------------

From the project root directory:

  cd ~/Projects/secure

Create the virtual environment:

  python3 -m venv .venv


------------------------------------------------------------
3. Activate the Virtual Environment
------------------------------------------------------------

Linux / macOS:

  source .venv/bin/activate

Your shell prompt should now show something like:

  (.venv) victor-reipur@DTU-5CG51911HW:~/Projects/secure$


------------------------------------------------------------
4. Install Dependencies
------------------------------------------------------------

Upgrade pip (recommended):

  python -m pip install --upgrade pip

Install required packages:

  pip install -r requirements.txt


------------------------------------------------------------
5. Run the Encryptor
------------------------------------------------------------

Example:

  python python/bw_encrypt.py bitwarden_export_example.json

This will generate:

  bitwarden_export_example_reipur_encrypted.json
  bitwarden_export_example_reipur_decryption_key.txt


------------------------------------------------------------
6. Decrypt (Optional)
------------------------------------------------------------

To decrypt an encrypted file:

  python python/bw_encrypt.py \
    bitwarden_export_example_reipur_encrypted.json \
    --decrypt \
    --keyfile bitwarden_export_example_reipur_decryption_key.txt


------------------------------------------------------------
7. Deactivate Virtual Environment
------------------------------------------------------------

When finished:

  deactivate


------------------------------------------------------------
SECURITY NOTES
------------------------------------------------------------

- The decryption key file MUST be kept secret
- Anyone with the key can decrypt all passwords
- Encrypted JSON files are NOT importable into Bitwarden
- This tool is intended for secure storage / transfer / archival

------------------------------------------------------------
