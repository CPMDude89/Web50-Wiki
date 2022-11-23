from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.urls import reverse
import markdown2

from . import util

# search bar on every page
class SearchForm(forms.Form):
    lookup = forms.CharField(label="Search Django's Encyclopedia")

# form to create a new page - see new_page()
class NewPageForm(forms.Form):
    newEntryTitle = forms.CharField(label="New Wiki Entry Title")
    newEntryContent = forms.CharField(label="New Wiki Entry", widget=forms.Textarea(attrs={
        "class": "col-10 form-control "
    }))

class EditPageForm(forms.Form):
    editedPage = forms.CharField(label="Edit Page", 
        initial="Test Value in instantiation",
        widget=forms.Textarea(attrs={
            "class": "col-10 form-control"
            }))

random_repeat_blocker = None


# homepage
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

# error page if something goes wrong, or a page is searched for that doesn't exist
def not_found(request):
    return render(request, "encyclopedia/not_found.html", {
        "form": SearchForm()
    })

# this is the primary view for users, this is the route used to display any wiki entry
# also has the default 'page not found' page if get_entry() returns a None
def page(request, title):
    # if get_entry() returns None, render 'page not found' route
    if not util.get_entry(title):
        return HttpResponseRedirect(reverse("not_found"), {
            "form": SearchForm()
        })
    
    # if get_entry() does find the page, open page.html and render the .md data via markdown2.markdown
    # will display the url as /ENTRYTITLE
    else:
        return render(request, "encyclopedia/page.html", {
            "title": title,
            "entry": markdown2.markdown(util.get_entry(title)),
            "form": SearchForm()
        })

def random_page(request):
    entry = util.find_random_entry()
    global random_repeat_blocker
    
    while True:
        if entry != random_repeat_blocker:
            break
        else:
            entry = util.find_random_entry()

    random_repeat_blocker = entry

    return HttpResponseRedirect(reverse("page", args=(entry,)))

# edit page --> designed to only be reached from ^^^ page() view
# uses 'initial', a django-specific parameter to set some 'initial' data in a form field 
def edit_page(request, entry):
    # if http request is post, returning the edited page
    if request.method == "POST":
        # send data back to server for validation by filling a new form with the user data
        edit_form = EditPageForm(request.POST)
        # check if the data is good
        if edit_form.is_valid():
            # use the data to create a newly edited page
            util.save_entry(entry, edit_form.cleaned_data["editedPage"])
            # go back to newly-edited page
            return HttpResponseRedirect(reverse("page", args=(entry,)),{
                "form": SearchForm(),
                "entry": entry,
                "edit_form": EditPageForm(initial={"editedPage": util.get_entry(entry)}) # newly-edited page
            })

    else:
        # instantiate the form with the initial data pre-populated into the textarea
        # which in this case, is the page we were just looking at, so we can edit the page we were just on
        edit_form = EditPageForm(initial={"editedPage": util.get_entry(entry)})
        # render the html file with the instantiated form so the user can edit the page
        return render(request, "encyclopedia/edit_page.html", {
            "form": SearchForm(),
            "entry": entry,
            "edit_form": edit_form
        })


### --- search function for wiki
def search(request):
    # if http request is 'POST', to send back user input (page to look up)
    if request.method == "POST":
        # send back to sever, the form populated with user data
        form = SearchForm(request.POST)
        # if django says the data is good
        if form.is_valid():
            # fill variable 'lookup' with user input -- the page user wants to see
            lookup = form.cleaned_data["lookup"]

            # if the get_entry() function returns a value, which means it found the page
            if util.get_entry(lookup):
                # render page.html, populated with the markdown data, converted to html by markdown2.markdown()
                # displays wiki page 
                # this is an important line I had to do some research on
                # return HttpResponseRedirect(reverse("page", kwargs={"title": lookup}), {     <--- this also works
                return HttpResponseRedirect(reverse("page", args=(lookup,)), {
                    "title": lookup,
                    "entry": markdown2.markdown(util.get_entry(lookup)),
                    "form": SearchForm()
                })
            
            # if get_entry() returns None, which means it didn't find a match with the search query and an existing wiki page
            # use check_lookup_spelling to see if there are any text fragments that could match a wiki entry
            # 'checks' user spelling, will return a list of links to entries that contain the text user entered into the search bar
            else:
                potential_entries = util.check_lookup_spelling(lookup)

                # if there is no fragment match, user will be redirected to a 'page not found' page
                if not potential_entries:
                    return HttpResponseRedirect(reverse("not_found"), {
                        "form": SearchForm()
                    })

                # will bring up 'search results' page, which will list all the potential entries, with links to their pages
                return render(request, "encyclopedia/search_results.html", {
                "potential_entries": potential_entries,
                "lookup": lookup,
                "form": SearchForm()
        })

        # if django says form data is 'not valid', send form back to user
        else: 
            return HttpResponseRedirect(reverse("not_found"), {
                "form": form
            })

### --- make a new page
def new_page(request):
    # if server receives 'POST' http request
    if request.method == "POST":
        # then fill the new page form with user inputted data
        newPageForm = NewPageForm(request.POST)
        # if django says the data is valid
        if newPageForm.is_valid():
            # fill variables 'title' and 'content' with user inputted data
            title = newPageForm.cleaned_data["newEntryTitle"]
            content = newPageForm.cleaned_data["newEntryContent"]

            # if there is not already an entry with that title, create a new page 
            if util.validate_title(title):  
                util.save_entry(title, content)
                
                # then finally redirect the user back to the homepage, via reverse()
                return HttpResponseRedirect(reverse("index"))

            # if there is already an entry with that title, reject form and send it back to the user
            # using 'invalid_title' to change an <h1> on the page letting the user know what happened
            else:
                return render(request, "encyclopedia/new_page.html", {
                "form": SearchForm(),
                "newPageForm": newPageForm,
                "invalid_title": True
                })


        # if django says the data is NOT valid, send back the form
        else:
            return render(request, "encyclopedia/new_page.html", {
                "form": SearchForm(),
                "newPageForm": newPageForm,
                "invalid_title": False
            })

    # if http request is 'GET', then send blank new page form
    return render (request, "encyclopedia/new_page.html", {
        "form": SearchForm(),
        "newPageForm": NewPageForm(),
        "invalid_title": False
    })
