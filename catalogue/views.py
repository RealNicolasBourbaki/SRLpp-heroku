from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from .models import CatalogueEntries
from .graph import make_graphs
from .forms import DocumentForm
from .models import SubmittedCatelogueEntries
from urllib.request import urlopen

import os
from io import BytesIO
import xml.dom.minidom
import xml.etree.ElementTree as ET
import zipfile
import boto3

ALL_DOWNLOAD_GROUP = []
SEARCH_DOWNLOAD_GROUP = []
SG_FILE = None
s3 = boto3.resource('s3', region_name=settings.AWS_S3_REGION_NAME)
bucket = s3.Bucket(settings.AWS_BUCKET)


def get_names(directory):
    """
    Returns a list of file names and a list of directories
    within the location of "directory"
    """
    contents = os.listdir(directory)
    files, directories = [], []
    for item in contents:
        candidate = os.path.join(directory, item)
        if os.path.isdir(candidate):
            directories.append(item)
        else:
            files.append(item)
    return files, directories


def _get_abs_virtual_root():
    return settings.PUBLISHED_CATALOGUE_DIR


def download(request, path):
    if os.path.exists(path):
        with open(path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
            return response
    raise Http404


def _make_zip(zip_subdir, files):
    zip_filename = "%s.zip" % zip_subdir
    s = BytesIO()
    zf = zipfile.ZipFile(s, "w")
    for fpath in files:
        key = os.path.relpath(fpath, start=settings.AWS_URL)
        subdir = os.path.relpath(key, start=settings.PUBLISHED_CATALOGUE_DIR)
        data = bucket.Object(key)
        zf.writestr(subdir, data.get('Body').read())
    zf.close()
    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp


def all_catalogue_download(request):
    global ALL_DOWNLOAD_GROUP
    for entry in _get_all_files_from_db():
        path = entry.entry_path
        ALL_DOWNLOAD_GROUP.append(path)

    if ALL_DOWNLOAD_GROUP:
        files = list()
        zip_subdir = "catalogue_entries"
        for file in ALL_DOWNLOAD_GROUP:
            files.append(file)
        resp = _make_zip(zip_subdir, files)
        return resp
    else:
        print('error here')
        raise TypeError("Files path are not set correctly.")


def search_download(request):
    global SEARCH_DOWNLOAD_GROUP
    if SEARCH_DOWNLOAD_GROUP:
        files = list()
        zip_subdir = "searched_catalogue_entries"
        for file in SEARCH_DOWNLOAD_GROUP:
            files.append(file)
        resp = _make_zip(zip_subdir, files)
        return resp
    else:
        raise TypeError("Files path are not set correctly.")


def _stylize_graphs(tree, file_path, target_graph_dir, content):
    global bucket
    prefix = os.path.relpath(target_graph_dir, settings.AWS_URL)+'/'
    images = bucket.objects.filter(Delimiter='/', Prefix=prefix)
    if images:
        content["graphs"] = [settings.AWS_URL+img.key for img in images]
    else:
        make_graphs(tree, file_path, settings.GRAPH_DIR)
        try:
            graphs = os.listdir(target_graph_dir)
            content["graphs"] = graphs
        except FileNotFoundError:
            content["graphs"] = None


class Content:
    def __init__(self):
        content = dict()
        type = None

    def define_basic_content(self, ):

        pass


def _view_file(request, file_path, mode):
    data = _list_directory(request, status='published')

    content = {
               'ordered_keys': data["ordered_keys"],
               'files': data["files"],
               'sub_dirs': data["sub_dirs"],
               'file_path': file_path
    }

    if mode == "style":
        tree = _get_xml_tree(file_path)
        styled_info = _get_xml_styled(tree)
        content["mode"] = mode
        target_graph_dir = os.path.join(settings.GRAPH_DIR, os.path.splitext(os.path.basename(file_path))[0])

        if styled_info:
            for key, val in styled_info.items():
                content[key] = val

        _stylize_graphs(tree, file_path, target_graph_dir, content)

    elif mode == "text":
        file_content = _get_xml_content(file_path)
        content["file_content"] = file_content
        content["mode"] = mode
        content["test"] = "test"
    return render(request, "catalogue/catalogue_view.html", content)


def _get_xml_content(xml_url):
    xml_string = []
    for line in urlopen(xml_url):
        xml_string.append(line.decode('utf-8'))
    xml_string = "\t".join(xml_string)
    dom = xml.dom.minidom.parseString(xml_string)
    file_content = []
    for line in dom.toprettyxml().split('\n'):
        if len(line.strip()) != 0:
            file_content.append(line)
    return file_content


def _get_xml_tree(xml_url):
    xml_string = []
    for line in urlopen(xml_url):
        xml_string.append(line.decode('utf-8'))
    xml_string = "\t".join(xml_string)
    return ET.ElementTree(ET.fromstring(xml_string))


def _get_xml_styled(tree):
    """
    De-serialization of xml files into dictionaries
    """
    try:
        concept = tree.getroot().find("concept")
        if concept:
            info = concept.find("info").attrib
            concept_id = info["id"]
            name = info["name"]
            version = info["version"]
            framenet_link = info["frameNetLink"] if "frameNetLink" in info.keys() else None
            roles = concept.find("roles")
            core_roles = [core_role.text for core_role in roles.findall("./coreRoles/coreRole")]
            non_core_roles = [non_core_role.text for non_core_role in roles.findall("./nonCoreRoles/nonCoreRole")]
            description = concept.find("description").text
            super_classes = [super_class.text for super_class in concept.findall("./superClasses/class")]
            examples = [example.text for example in concept.findall("./examples/example")]
            if not examples:
                examples = ["None"]
            style_content = {
                "concept_id": concept_id,
                "name": name,
                "version": version,
                "core_roles": core_roles,
                "non_core_roles": non_core_roles,
                "description": description,
                "super_classes": super_classes,
                "examples": examples
            }
            if framenet_link:
                style_content["framenet_link"] = framenet_link
        else:
            style_content = None
    except Exception:
        raise ValueError("xml file poorly constructed!")
    return style_content


def _get_link_target(path):
    link_target = os.path.relpath(path, start=settings.PUBLISHED_CATALOGUE_DIR)
    return link_target


def _to_lower(text):
    return text.lower()


def _make_sort_key(subdir, basename):
    if subdir == '':
        sort_key = os.path.splitext(basename)[0]
    else:
        sort_key = subdir
    return sort_key


def _sort_all_keys(all_files_info, all_dir_info):
    key_order = sorted(list(all_files_info.keys()) + list(all_dir_info.keys()))
    return key_order


def _get_all_files_from_db(status="published"):
    return list(CatalogueEntries.objects.all())


def _list_directory(request, status='published'):
    if check_access(request):
        if status == 'published':
            all_files_info = {}
            all_dir_info = {}
            global ALL_DOWNLOAD_GROUP
            ALL_DOWNLOAD_GROUP.clear()
            for entry in _get_all_files_from_db():
                path = entry.entry_path
                basename = entry.entry_name
                subdir = entry.belongs_to_sub_directory
                sort_key = _make_sort_key(subdir, basename)
                link_target = subdir+"/"+basename
                ALL_DOWNLOAD_GROUP.append(path)
                if subdir == '':
                    all_files_info[sort_key] = (link_target, basename)
                else:
                    if sort_key not in all_dir_info.keys():
                        all_dir_info[sort_key] = [
                            (link_target, basename)]
                    else:
                        all_dir_info[sort_key].append(
                            (link_target, basename))

            for key, val in all_dir_info.items():
                all_dir_info[key] = [
                    tup for tup in sorted(
                        val, key=lambda v:v[1])]
            ordered_keys = _sort_all_keys(
                all_files_info, all_dir_info)
            data = {
                'ordered_keys': ordered_keys,
                'files': all_files_info,
                'sub_dirs': all_dir_info,
            }
            return data
    raise PermissionError


def check_access(request):
    """Check if the user has proper access"""
    return True


def browse(request, path, mode):
    """Directory list view
    There is a possibility that this function is going to be used somewhere else
    In which case, there should be an independent app in the project
    But we'll see if there's this need. I'll change accordingly.
    """
    catalogue_path = os.path.join(settings.PUBLISHED_CATALOGUE_DIR, path)

    if catalogue_path.endswith('.xml'):
        if mode == "":
            mode = "text"
        return _view_file(request, catalogue_path, mode)
    else:
        return render(
            request,
            'catalogue/catalogue_view.html',
            _list_directory(
                request, status='published'))
    # If the path points to a file, view it. If not, list out files in the
    # directory


def _search_files(request, query):
    matched_files_links = []
    global SEARCH_DOWNLOAD_GROUP
    SEARCH_DOWNLOAD_GROUP.clear()
    if len(query.strip()) != 0:
        all_files_info = _get_all_files_from_db()
        all_files_path_name = [(os.path.join(settings.PUBLISHED_CATALOGUE_DIR, p.entry_path), p.entry_name)
                               for p in all_files_info]
        for file_path, file_basename in all_files_path_name:
            if query in file_path.lower():
                matched_files_links.append(
                    (_get_link_target(file_path), file_basename))
                SEARCH_DOWNLOAD_GROUP.append(file_path)
        if len(matched_files_links) != 0:
            data = {
                'search_results': matched_files_links,
                'original_query': query
            }
        else:
            data = {
                'no_results': ['Ops, no search results. Click me to go back to catalogue']}
    else:
        data = _list_directory(request)
    return data


def search(request):
    srh = request.GET['query'].lower()
    data = _search_files(request, srh)
    return render(request, 'catalogue/catalogue_view.html', data)


def search_view(request, link, query):
    data = _search_files(request, query)
    file_path = os.path.join(_get_abs_virtual_root(), link)
    if link:
        content = _get_xml_content(file_path)
        data['file_content'] = content
        data['file_path'] = file_path
    return render(request, 'catalogue/catalogue_view.html', data)


def generate_sg(file_path, name):
    tree = _get_xml_tree(file_path)
    out_path = settings.TEMP_DIR
    make_graphs(tree, file_path, out_path)
    try:
        graphs = os.listdir(out_path.joinpath(name[:-4]))

    except FileNotFoundError:
        graphs = []
    return graphs


def _handle_uploaded_file(f, name):
    with open(settings.TEMP_DIR.joinpath(name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def submit_sg_generation(request):
    global SG_FILE
    message = 'Please select the file for Semantic Graph generating.'
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            SG_FILE = request.FILES['docfile']
            _handle_uploaded_file(SG_FILE, SG_FILE.name)
            redirect('generate_sg')
        else:
            message = 'The form is not valid. Fix the following error:'
    else:
        form = DocumentForm()
    if SG_FILE:
        file_path = settings.TEMP_DIR.joinpath(SG_FILE.name)
        graphs = generate_sg(file_path, SG_FILE.name)
    else:
        file_path = None
        graphs = None
    content = {'graphs': graphs, 'form': form, 'message': message, 'file_path': file_path}
    return render(request, 'catalogue/catalogue_sg.html', content)


def upload_file(request):
    message = 'Please upload a single file or a zipped file.'
    # Handle file upload
    if request.user.is_authenticated:
        username = request.user.username
        user_email = request.user.email
    else:
        username = None
        user_email = None
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = SubmittedCatelogueEntries(docfile=request.FILES['docfile'])
            newdoc.set_uploader(username, user_email)
            newdoc.save()

            # Redirect to the document list after POST
            return redirect('submit')
        else:
            message = 'The form is not valid. Fix the following error:'
    else:
        form = DocumentForm()  # An empty, unbound form

    # Load documents for the list page
    documents = [doc for doc in SubmittedCatelogueEntries.objects.all() if doc.username == username]

    # Render list page with the documents and the form
    context = {'documents': documents, 'form': form, 'message': message}
    return render(request, 'catalogue/upload_annotation.html', context)
