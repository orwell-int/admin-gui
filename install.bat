git submodule update --init --recursive

cd client
call install.bat
cd ..

cd server
call install.bat
cd ..

pause