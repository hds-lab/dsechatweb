# AutoDomain
Automatically append a preset domain to the username.

## Usage
To enable *AutoDomain* you have to include its JavaScript code:

```HTML
<script type="text/javascript" src="candyshop/auto-domain/candy.js"></script>
```

Call its `init()` method after Candy has been initialized:

```JavaScript
Candy.init('/http-bind/');

// enable AutoDomain plugin (you must specify the domain)
CandyShop.AutoDomain.init({
    xmppDomain: 'xmpp.example.com'
});

Candy.Core.connect();
```

Now, when the user enters their username, the domain will be automatically added.
