# Py4Web_DEAL
Py4Web Datatables Editor Ajax Library (Full CRUD)

Ok, the first implementation is now ready - needs testing if anyone wants to use it. Message me and I will send a copy, I plan to put this into a GitHub Repository

This library serves up AJAX data to the DataTables and/or Editor libraries. It can be used to simply get AJAX data to show a Datatables Table (free), or add full CRUD capabilities with an Editor license. (https://editor.datatables.net/)

How it works:

With this library you setup a datatables Editor config in your html file with corresponding javascript for that table, (its not difficult) and setup how you want the DataTable Editor to look and act. It calls this AJAX library via a controller function, which handles all AJAX for complete CRUD between the Datatables Editor and py4web in a single line.

In this example for the db.t_question table. (Only tables and queries of that table at the moment, it doesn't handle CRUD for joined queries.)

return dteditor_data(db.t_question, request, <optional query>)

It does everything, all CRUD functions including image upload and reference table lookup, with all reference options and selections.

 There is minimal entry into the controller.py, literally just two lines. However, you do need to lay out the table in the html template and setup the javascript, as per the Datatables Editor instructions, but if you follow the below example it is easy. 

In the controller we have two sections, the first is for the actual template page e.g. questions.html the second is for the Ajax data question_data. (This is called by the datatable and editor) - thats it!

Let me know if you find a use for this and if you find any bugs.

###########################################################
### USAGE
##########################################################
Put this file in /<project folder>/libs/
In your models.py it is Recomended to use a format field correctly set in reference tables. E.g. format='%(name)s', so that the selection options can use this to display in drop downs etc.

MODELS.PY:
########################################
db.define_table('group',
    Field('name', type='string', unique=True,
          label=T('Name')),
    Field('f_desc', type='string',
          label=T('Description')),
    format='%(name)s',
    )
db.define_table('t_video',
    Field('f_name', type='string',
          label=T('Name')),
    Field('f_desc', type='string',
          label=T('Description')),
    Field('group', type='reference group',
          label=T('Group')),
    Field('f_vimeoid', type='string', label=T('VimeoID')),
    format='%(f_name)s',
)

CONTROLLER.PY:
########################################
from .libs.datatables_API import dteditor_data

@action("video", method=["GET", "POST"])
@action.uses(session, db, auth.user, "videos.html")
def video():
    page_title = 'Videos'
    page_subtitle = 'Videos'

    return dict(page_title=page_title, page_subtitle= page_subtitle)

@action('video_data', method=['GET', 'POST'])
@action.uses(session, db, auth.user)
def video_data():
    table = db.t_video
    return dteditor_data(table, request)

TEMPLATE: questions.html:
You need to lay out the datatables in javascript, E.G.
Download and install Editor
########################################
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/v/bs4-4.1.1/jq-3.3.1/jszip-2.5.0/dt-1.10.24/af-2.3.5/b-1.7.0/b-colvis-1.7.0/b-html5-1.7.0/b-print-1.7.0/cr-1.5.3/date-1.0.3/fc-3.3.2/fh-3.1.8/kt-2.6.1/r-2.2.7/rg-1.1.2/rr-1.2.7/sc-2.0.3/sb-1.0.1/sp-1.2.2/sl-1.3.3/datatables.min.css"/>
    <link rel="stylesheet" type="text/css" href="DataTables/Editor-2.0.1/css/editor.bootstrap4.css"/>

<div class="container-fluid">
  <div class="row">
    <div class="col-sm w-98 p-2 border">
        <h1>questions</h1>
        <table id="questions" class="table table-bordered table-sm table-hover" style="width:100%">
            <thead>
                <tr >
                    <th data-toggle="tooltip" data-placement="top" title="Name">Name</th>
                    <th data-toggle="tooltip" data-placement="top" title="Description">Desc</th>
                    <th data-toggle="tooltip" data-placement="top" title="Group">Group</th>
                    <th data-toggle="tooltip" data-placement="top" title="Picture">Picture</th>
                </tr>
            </thead>
        </table>
    </div>
  </div>
</div>
<script>
var editor; // use a global for the submit and return data rendering in the examples

$(document).ready(function() {
    ///////////////////////////////////////////////////////
    //question
    ///////////////////////////////////////////////////////
    var questionEditor = new $.fn.dataTable.Editor
    ({
        ajax: {
            url: "/MindTrax/question_data",
            data: function (d) {
                var selected = questionTable.row({selected: true});
                if (selected.any()) {
                    d.question = selected.data().t_question.id;
                }
            }
        },
        table: '#questions',
        idSrc: "t_question.id",
        fields: [
            {
                label: "Name:",
                name: "t_question.f_name",
            },
            {
                label: "Desc:",
                name: "t_question.f_desc",
            },
            {
                label: "group:",
                name: "group.name",
                type: "select",
            },
            {
                label: "Picture:",
                name: "t_question.picture",
                type: "upload",
                display: function (file_id) {
                    return file_id ?
                        '<img src="'+ '/MindTrax/downloadfile/t_question_'+ file_id.toString() + '.png" width="25" height="25">' :
                        null;
                },

            },
            ]
        }
    );

    var questionTable = $('#questions').DataTable
    ( {
        dom: 'BfrtipQ',
        ajax: "/MindTrax/question_data",
        idSrc: "t_question.id",
        columns: [
            { data: 't_question.f_name',
                title: "Name",
            },
            { data: 't_question.f_desc',
                title: "Description",
            },
            { data: "group.name" },
            { data: "t_question.picture",
                  render: function ( file_id ) {
                    return file_id ?
                        '<img src="/MindTrax/downloadfile/t_question_' + file_id.toString() + '.png" width="25" height="25">' :
                        null;
                },
                defaultContent: "No image",
                title: "Image",
                },
            ],
        select: {
            style: 'single'
        },
        buttons: [
            { extend: 'create', editor: questionEditor },
            { extend: 'edit',   editor: questionEditor },
            { extend: 'remove', editor: questionEditor },
        ],
    } );



});
</script>
    <script type="text/javascript" src="https://cdn.datatables.net/v/bs4-4.1.1/jq-3.3.1/jszip-2.5.0/dt-1.10.24/af-2.3.5/b-1.7.0/b-colvis-1.7.0/b-html5-1.7.0/b-print-1.7.0/cr-1.5.3/date-1.0.3/fc-3.3.2/fh-3.1.8/kt-2.6.1/r-2.2.7/rg-1.1.2/rr-1.2.7/sc-2.0.3/sb-1.0.1/sp-1.2.2/sl-1.3.3/datatables.min.js"></script>
    <script type="text/javascript" src="DataTables/Editor-2.0.1/js/dataTables.editor.js"></script>
    <script type="text/javascript" src="DataTables/Editor-2.0.1/js/editor.bootstrap4.js"></script>


