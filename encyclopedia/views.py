import random
import markdown2
from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    """
    Render a page that displays the contents of encyclopedia entry of that title
    """
    entry_content = util.get_entry(title)
    if entry_content is None:
        # Render error page
        return render(request, "encyclopedia/error.html", {
            "error_message": "The requested page was not found."
        })
    else:
        # Render the page for the requested title
        entry_html = markdown2.markdown(entry_content)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": entry_html
        })
    
def search(request):
    """
    Allow the user to type q query into search box to search for an encyclopedia entry.
    """
    query = request.GET.get('q', '')
    print(query)
    entries = util.list_entries()
    print(entries)
    if query in entries:
        # If the query matches an entry exactly, redirect to that entry's page
        return redirect('entry', title=query)
    else:
        # Otherwise, find all entries that contain the query as a substring
        matches = [entry for entry in entries if query.lower() in entry.lower()]
        return render(request, 'encyclopedia/search_results.html', {'matches': matches})


class NewPageForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100)
    content = forms.CharField(widget=forms.Textarea, label="Content")

def create(request):
    """
    Create a new encyclopedia entry
    """
    if request.method == "POST":

        # Take in the data the user submitted and save it as form
        form = NewPageForm(request.POST)
        # print(form)

        # Check if form data is valid (server-side)
        if form.is_valid():
            # print(form.cleaned_data)

            # Isolate the title & content from the 'cleaned' version of form data
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # Check if the entry with the same title already exists
            if util.get_entry(title) is not None:
                # Display an error message
                messages.error(request, "An entry with this title already exists.")
            else:
                util.save_entry(title, content)
                # redirect to the new page
                return redirect('entry', title=title)
    else:
        form = NewPageForm()

    return render(request, "encyclopedia/create.html", {
        "form": form
    })


# first get the title and content of entry
# get the html
# populate the title content with the above text

class EditPageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, label='')

def edit(request, title):
    """
    edit the current page the user is seeing
    """
    # Get the content of that entry
    entry = util.get_entry(title)

    if entry is None:
        return render(request, "encyclopedia/error.html", {"title": title})

    if request.method == "POST":
        form = EditPageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            messages.success(request, 'Your changes have been saved.')
            return redirect('entry', title=title)

    else:
        form = EditPageForm(initial={'content': entry})

    return render(request, "encyclopedia/edit.html", {
        "form": form,
        "title": title
    })

def random_page(request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return redirect('entry', title=random_entry)

