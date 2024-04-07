pip install virtualenv
call .\chatweb\Scripts\activate.bat
pip install -r .\requirements.txt
python .\main.py %*
pause