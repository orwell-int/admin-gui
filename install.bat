git submodule update --init --recursive

rem cd client
rem call install.bat
rem cd ..

cd server
call install.bat
cd ..