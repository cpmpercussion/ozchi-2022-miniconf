## OzCHI 2022 Webpage using MiniConf

This is the website to the 2022 OzCHI Conference.

The website uses the <a href='https://github.com/Mini-Conf/Mini-Conf'>"miniconf"</a> system. Go look there to see miniconf specific documentation.

This readme is the documentation from Miniconf for how to configure tand develop the page.

## How to serve locally:

<pre>
> python3 -m pip install -r requirements.txt
> make run
</pre>

When you are ready to deploy run `make freeze` to get a static version of the site in the `build` folder. 
