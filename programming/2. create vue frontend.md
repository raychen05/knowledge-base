
#### To create a simple Vue.js Frontend


1. Set Up the Frontend with Vue.js

```bash

    # -------------------------
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    pip install jaydebeapi
    # Use the WOS Dev Cluster "WOS Dev Cluster - UC Enabled"

    #------------------------

    install dependencies
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
  
    brew install node
    npm install -g npm@latest
    # Vue CLI
    npm install -g @vue/cli
    npm install axios



    # setup env
    eval "$(/opt/homebrew/bin/brew shellenv)"
    source ~/.zprofile         

    node -v
    npm -v

    brew --version

```

2. Create a New Vue Project: 

```bash
    vue create typeahead-search
    cd typeahead-search

```

3. Run the Vue App
```bash
    npm run serve
```

4.  Test the Application - Endpoint

 http://localhost:8080 

