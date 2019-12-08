# admin-gui

## Description

Interface that allows to configure Orwell

## Usage

**Nothing yet**

## Development

### Introduction

The project is divided in two parts the client and the server.

You should start by installing some dependencies.

```shell script
install.bat
```

If installation works fine, building should then be possible.

```shell script
build.bat
```

If building works fine, starting should the be possible.

```shell script
start.bat
```

### Client

This part is developed in TypeScript.

Quick notes about development environment:
-choco install nvm
-nvm install latest
-nvm use 12.11.1
-choco install yarn

Running the client:
-cd client/admin-app
-yarn
-yarn ng build --prod
-yarn start

VSCode extensions:
-eslint
-prettier
-material icon theme
-debugger for Chrome
-angular snippets

### Server

This part is developed in Python (version 3).
