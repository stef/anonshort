# Anonshort

## tl;dr
Anonshort shortened URL resolverer that keeps you from being click-tracked with URL-shortener services (let's call them USSes from now on) that can be considered evil. This is a web-based redirector service that keeps your ass untracked.

## Status
Anonshort is currently in the phase of declaring the requirements. User-agent collection code is WIP for pretending a browser for fetching URLs.

## Motivation
Nowadays every major web company operates its own URL-shortening service (fb.me, goog.gl, t.co etc.) that they (can) use to track user exit behaviour. While this has a real advantage of shortening URLs, some of this companies are using them to track individual user behaviour.

## Features

* Prevents linkrotting/decaying as it remembers URLs that have been removed from the original USSes.
* Pretends to be an ordinary browser, none of your headers or IP-address are forwarded.

## Operation

### Front end

The service should be able to operate in two modes:

* Directed: as a regular HTTP service with it's own DNS-based FQDN entry (http://unshorten.somedomain.com/t.co/someurl)
* Transparent: it's a kind of impersonation mode so to speak, where the service answers the queries just as if it were the original shortening service. This way DNS entry is not needed, but there's a need for client side /etc/hosts to reach the service point. Think of your home OpenWRT gateway serving DNS records for your non-rooted Android/iPhone/etc devices to point to this service instead of the original USS.

### Fetching

The service should pretend itself to be a decent browser. Some statistical user-agent forging may be needed. Official APIs may be used [iif](http://en.wikipedia.org/wiki/If_and_only_if) it is fully anonymous (no need to register for an API key at all).

### Caching

Every successful (and static) request should be inserted into a database, so further queries to the same shortened URL can be delivered from the database, also this makes click-tracking futile for the original shortening service. There are known USS that enables to change the short URLs, I'd call these USSes dynamic, some periodic checking of short URLs should be implemented.

### Multiple unshortening

There are cases when 3 or 4 different shortening services are involved in chain for presenting an URL, like on some tweets (t.co -> bit.ly -> etc). Anonshort should handle these multiple redirections internally (fetching each of the USSes within the same client query) and presend the final known URL to the client.

## Design considerations

Some plugin architecture should be kept in mind to allow for 3rd parties extension of the service with ease. Python provides methods for this, like using decorators (@service("t.co"):)
Inheritable base python classes should be provided with general type of shortener services.

## Possible problems

### Privacy on the service side
Webserver access logs with anonymity? Log just the used USS but not the actual short url?

### HTTPS
Some service (notably t.co) may utilize SSL-wrapped HTTP to protect the transaction, thus it's a bit harder to impersonate the service on the Anonshort side. One solution is that a "trusted" (self|own CA)signed SSL certificate may be generated. The other way would be client side degradation of HTTPS to HTTP (it can be done Redirector described later).

### Redirect loops
Circular references may happen on multiple lookups. This should be detected and avoided so that Anonshort does not go into an endless loop. 
Sometimes, however, a mistake can cause the redirection to point back to the first page, leading to an infinite loop of redirects. Browsers usually break that loop after a few steps and display an error message instead.

The [HTTP standard](http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.3) states:

* A client SHOULD detect infinite redirection loops, since such loops generate network traffic for each redirection.
* Previous versions of this specification recommended a maximum of five redirections; some clients may exist that implement such a fixed limitation.

### Blocking of Anonshort by USSs
Sooner of later it will happen :) Consider moving Anonshort behind Tor to get rid of the per IP-Address blocks of USSes.

### Cooperation between individual instances of Anonshort?
In the far future, db syncing Just like seeks does it? Some protection against roughe Anonshort instances should be implemented.

### Users with no admin rights to modify /etc/hosts
Provide them with browser addons like the [Redirector](https://addons.mozilla.org/en-US/firefox/addon/redirector/) for Firefox. It can be used to seamlessly redirect queries directoed to USSes to the directed frontend interface of Anonshort.

## Types of redirection
### Standard methods
Classes for standard redirection methods can be the base for further inheritation.

* HTTP Location header
* HTTP Refresh header
* HTML META refresh tag
* Javascript location.replace()

## Further variations in the wild
Altough it's not the main tasks to deal with Referrer Masking Services (RMS) or Link Protection Services (LPS), one may encounter a service that has URL hashing or sequencing on these sites. Anonshort plugin architecture could be used to interface Anonshort to this services.

### Referrer Masking Services: Added Complexity. 
Redirection services can hide the referrer by placing an intermediate page between the page the link is on and its destination. Although these are conceptually similar to other URL redirection services, they serve a different purpose, and they rarely attempt to shorten or obfuscate the destination URL (as their only intended side-effect is to hide referrer information and provide a clear gateway between other websites.)
### Framed redirects
### CAPTCHAs
lix.in does it for example. 

## Similar projects

* [swizec's](http://swizec.com/blog/) [node-unshortener](http://swizec.com/blog/node-unshortener-can-unshort-any-url/swizec/1763) on [github](https://github.com/Swizec/node-unshortener)

