# Copyright 2021 Richard Behan-Howell
# Written by Richard Behan-Howell
# All rights reserved
from ..common import db, Field, T, auth
import json
from datetime import datetime
from yatl.helpers import SCRIPT, XML
import re
from py4web import action, request, abort, redirect, URL, Field, DAL, response
import os
from .. import settings

###########################################################
### USAGE
##########################################################
# Put this file in /<project folder>/libs/
# Recomended to use a format field correctly set in reference tables. E.g. format='%(name)s',
# in the controller, use this format, for example a video table.
"""
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

"""

###################################
#Helper functions
###################################
def format(table, row):
    if not row:
        return T('Unknown')
    elif isinstance(table._format, str):
        return table._format % row
    elif callable(table._format):
        return table._format(row)
    else:
        return '#' + str(row.id)

def plural(table):
    return table._plural or pluralize(table._singular.lower()).capitalize()

def right(s, amount):
    if s == None:
        return None
    elif amount == None:
        return None # Or throw a missing argument error
    s = str(s)
    if amount > len(s):
        return s
    elif amount == 0:
        return ""
    else:
        return s[-amount:]


###################################
# table_format_reference_list(table):
#
# Pass in a table e.g. db.group
# Assumes that the table has a format field correctly set. E.g. format='%(name)s',
# Generates a JSON list of lookup references from a table. format and id.
# E.G. [{'label': 'Inadequate', 'value': 2}, {'label': 'Confused2', 'value': 3}, {'label': 'Hurt', 'value': 4}]
# ###################################
def table_format_reference_list(table):
    #print("table list: "+ table._tablename+ "\r")
    #print("table format:" + db[table]._format)

    list = []
    query = (table.id > 0)
    if db(table).isempty():
        data = ["empty"]
    else:
        if db(table.id > 0).count() > 0:
            for z in db(query).select():
                list.append({'label': format(table, z), 'value': z.id})


    print("list:" + str(list))
    return list

"""
def record_data(table, z):
    if z:
        return {
            "DT_RowId":"row_" + str(z.id),
            table._tablename: {
                "id":z.id,
                "name":z.name,
                "code":z.code,
            }
        }
    else:
        return []
"""

###################################
# files_record_data(table, z):
#
# Pass in a table e.g. db.group and row
# Assumes that the table has a format field correctly set. E.g. format='%(name)s',
####################################
def files_record_data(table, z):
    if z:
        return {
            str(z.id): {
                "id": str(z.id),
                "name": format(table, z),
                "filename": z.filename,
                "filesize": z.filesize,
                "web_path": z.web_path,
                "system_path": z.system_path,
            }
        }
    else:
        return []




###################################################################################################
## OPTIONS
####################################################################################################
def generic_options(table):
    # Takes a Table, finds any reference fields and populates a dictioanry of the [possible names and id for each reference field.
    #return: {"grower.name":table_format_reference_list(db.grower),"variety.name":table_format_reference_list(db.variety),"branch.name":table_format_reference_list(db.branch)}

    fields = [dict(name=f.name, type=f.type) for f in table if f.readable]
    optiondict = {}

    for f in fields:
        if 'reference' in f.get('type'):
            # get the name of the Field. I.e. grower_id
            fieldname = f.get('type').split()[0]
            # get the name of the reference table. I.e. Grower
            reftable = f.get('type').split()[1]
            #Get a list of name and id from that table using helper function table_format_reference_list
            #print("reftable.format: " + str(db[reftable]._format) + '\r')

            for t in db:
                if reftable == t._tablename and reftable != 'upload' and reftable != 'auth_user':
                    print("t._tablename: " + str(t._tablename) + '\r')
                    print("table: " + str(db[reftable]._tablename) + '\r')
#                    print("%(name)s" % db[reftable].name)

                    optiondict.update({f.get('name')+str('.name'): table_format_reference_list(db[reftable])})
    #               {reftable: {'name': getattr(z, f.get('name')).name if getattr(z, f.get('name')) else 'Null'}})
                elif reftable == t._tablename and reftable == 'auth_user':
                    print("t._tablename: " + str(t._tablename) + '\r')
                    print("table: " + str(db[reftable]._tablename) + '\r')
                    optiondict.update({f.get('name') + str('.username'): table_format_reference_list(db[reftable])})
    #               {reftable: {'name': getattr(z, f.get('name')).name if getattr(z, f.get('name')) else 'Null'}})

        print("options tablelist: " + str(optiondict) + '\r')
    return optiondict


############################################################################
# generic_record_data
#############################################################################
def generic_record_data(table, z):
    fieldlist = []
    if z:

        fields = [dict(name=f.name, type=f.type) for f in table if f.readable]
        record = {}
        reflist = []
        for f in fields:
            #finalise all types of fields
            if (f.get('type') == "datetime"):
                try:
                    record.update({f.get('name'): z[f.get('name')].strftime('%Y-%m-%d')})
                except:
                    record.update({f.get('name'): ""})
            elif f.get('type') == "boolean":
                record.update({f.get('name'): '1' if getattr(z, f.get('name')) else '0'})
            elif 'reference' in f.get('type'):
                record.update({f.get('name'): getattr(z, f.get('name'))})
                reftable = f.get('type').split()[1]

                # grower=dict(name=z.grower_id.name if z.grower_id else 'Null'),
                f.get('name')
                reflist.append(
                    {f.get('name'): {'name': getattr(z, f.get('name')).name if getattr(z, f.get('name')) else 'Null'}})
            else:
                record.update({f.get('name'): getattr(z, f.get('name'))})
        #print("record: " + str(record) + '\r')
        #print("reflist: " + str(reflist) + '\r')

        data = {}
        data.update({'DT_RowId':'row_' + str(z.id), table._tablename: record})


        #Iterate through all reference fields and fill in their "name option.
        for ref in reflist:
            data.update(ref)

        return data
    else:
        return []


def dteditor_data(table, request, query=None):
    """
    datatables.net makes an ajax call to this method to get the data
    1. read
    Send back JSON about the table with all records and the referenced fields in the format:

    2. create
    3. edit
    4. remove

    :return:
    """
    print("dteditor_data request method" + str(request.method))
    data = []
    files = []
    files_dict = {}
    option = []
    if query is None:
        query = (table.id > 0)
    if request.method == 'GET':
        #iterate through any fields here that are reference fields.

        options = generic_options(table)
            #{"grower.name":table_format_reference_list(db.grower),"variety.name":table_format_reference_list(db.variety),"branch.name":table_format_reference_list(db.branch)}



        if db(table).isempty():
            data = []
            files = []
        else:
            if db(table.id > 0).count() > 0:
                data = [generic_record_data(table,z) for z in db(query).select()]

            for z in db(db.upload.table == table).select():
                files_dict.update(files_record_data(db.upload,z))

            files = {"files": files_dict}

            #formulate the response:

        return json.dumps(dict(data=data,options=options,files=files), indent=4, sort_keys=False, default=str)

    elif request.method == 'POST':
        action = request.forms.get("action")
        print("action: " +str(action))
        if action=="create":
            kwargs = {}
            #Need to iterate through the table fields looking for data for each, if nothing exists then ignore it, if it does then set it.
            fields = [dict(name=f.name, type=f.type) for f in table if f.readable]
            for f in fields:
                # finalise for all types of fields
                    # datetime, date, time
                    if (f.get('type') == "datetime") or (f.get('type') == "date") or (f.get('type') == "time"):
                        for key in request.forms.keys():
                            if "data[0]["+table._tablename+"][" + f.get('name') + "]" in key:
                                print("if " + "data[0]["+table._tablename+"][" + f.get('name') + "]" + " in key")
                                print("True key:" + key)
                                try:
                                    dt = datetime.strptime(request.forms.get("data[0]["+table._tablename+"][" + f.get('name') + "]"), '%Y-%m-%d').date()
                                    kwargs.update({f.get('name'): dt})
                                except:
                                    print("Datetime format error:" + request.forms.get("data[0]["+table._tablename+"][" + f.get('name') + "]"))
                                    pass
                    elif (f.get('type') == "boolean"):
                        for key in request.forms.keys():
                            if "data[0]["+table._tablename+"][" + f.get('name') + "]" in key:
                                print("if " + "data[0]["+table._tablename+"][" + f.get('name') + "]" + " in key")
                                print("True key:" + key)
                                try:
                                    kwargs.update({f.get('name'): True if ( request.forms.get("data[0]["+table._tablename+"][" + f.get('name') + "]") == "1") else False})
                                except:
                                    pass

                    elif 'reference' in f.get('type'):
    #                        reftable = f.get('type').split()[1]
                        for key in request.forms.keys():
                            if "data[0][" + f.get('name') + "][name]" in key:
                                print("if " + "data[0][" + f.get('name') + "][name]" + " in key")
                                print("True key:" + key)
                                try:
                                    kwargs.update({f.get('name'): int(request.forms.get("data[0][" + f.get('name') + "][name]"))})
                                except:
                                    pass


                    #Integers,
                    elif ((f.get('type') == "blob") or (f.get('type') == "integer") or (f.get('type') == "double")
                          or (f.get('type') == "bigint") or ('decimal' in f.get('type'))):
    #                       blob, integer, double, decimal(n, m), bigint
                        for key in request.forms.keys():
                            if "data[0]["+table._tablename+"][" + f.get('name') + "]" in key:
                                print("if " + "data[0]["+table._tablename+"][" + f.get('name') + "]" + " in key")
                                print("True key:" + key)
                                try:
                                    kwargs.update({f.get('name'): int(request.forms.get("data[0]["+table._tablename+"][" + f.get('name') + "]"))})
                                except:
                                    pass


                    else:
                        #Stinrg, Text, password, json
                        for key in request.forms.keys():
                            if "data[0]["+table._tablename+"][" + f.get('name') + "]" in key:
                                print("if " + "data[0]["+table._tablename+"][" + f.get('name') + "]" + " in key")
                                print("True key:" + key)
                                try:
                                    kwargs.update({f.get('name'): request.forms.get("data[0]["+table._tablename+"][" + f.get('name') + "]")})
                                except:
                                    pass

            print("kwargs:" + str(kwargs)+"\r\r")

            #grower_id = request.forms.get("data[0][grower_id][name]")
            #variety_id = request.forms.get("data[0][variety_id][name]")
            #branch_id = request.forms.get("data[0][branch_id][name]")
            #commencement_dt = datetime.strptime(request.forms.get("data[0][growercontract][commencement_dt]"), '%Y-%m-%d').date()
            #expiry_dt = datetime.strptime(request.forms.get("data[0][growercontract][expiry_dt]"), '%Y-%m-%d').date()
            #name = db.grower[grower_id].name + ',' + db.variety[variety_id].name + ',' + db.branch[branch_id].name
            #contract_id = request.forms.get("data[0][growercontract][contract_id]")
            #contractsigned = True if (request.forms.get("data[0][growercontract][contractsigned]")=="1") else False

            #Create new
            #Do other specific error checking here.
            newid = table.insert(**kwargs)
            """
            newid = table.insert(
                name = name,
                grower_id=grower_id,
                variety_id=variety_id,
                branch_id=branch_id,
                commencement_dt=commencement_dt,
                expiry_dt=expiry_dt,
                contract_id=contract_id,
                contractsigned=contractsigned,
            )
            """
            print("newid: "+str(newid))
            db.commit()
            z = db(table.id == int(newid)).select().first()
            data = [generic_record_data(table,z)]
            return json.dumps(dict(data=data), indent=4, sort_keys=True, default=str)
        elif action == "edit":
            id = 0
            for key in request.forms.keys():
                if "data" in key:
                    try:
                        a = key.split('[')
                        #print(str(a))
                        id = int(a[1].strip("]["))
                        print("id:"+str(id))
                        break
                    except:
                        return
            #id = request.forms.get("growercontract")
            kwargs = {}
            # Need to iterate through the table fields looking for data for each, if nothing exists then ignore it, if it does then set it.
            fields = [dict(name=f.name, type=f.type) for f in table if f.readable]
            for f in fields:
                # finalise for all types of fields
                # datetime, date, time
                if (f.get('type') == "datetime") or (f.get('type') == "date") or (f.get('type') == "time"):
                    for key in request.forms.keys():
                        if "data["+str(id)+"][" + table._tablename + "][" + f.get('name') + "]" in key:
                            print("if " + "data["+str(id)+"][" + table._tablename + "][" + f.get('name') + "]" + " in key")
                            print("True key:" + key)
                            try:
                                dt = datetime.strptime(
                                    request.forms.get("data["+str(id)+"][" + table._tablename + "][" + f.get('name') + "]"),
                                    '%Y-%m-%d').date()
                                kwargs.update({f.get('name'): dt})
                            except:
                                print("Datetime format error:" + request.forms.get(
                                    "data["+str(id)+"][" + table._tablename + "][" + f.get('name') + "]"))
                                pass
                elif (f.get('type') == "boolean"):
                    for key in request.forms.keys():
                        if "data["+str(id)+"][" + table._tablename + "][" + f.get('name') + "]" in key:
                            print("if " + "data["+str(id)+"][" + table._tablename + "][" + f.get('name') + "]" + " in key")
                            print("True key:" + key)
                            try:
                                kwargs.update({f.get('name'): True if (request.forms.get(
                                "data["+str(id)+"][" + table._tablename + "][" + f.get('name') + "]") == "1") else False})
                            except:
                                pass

                elif 'reference' in f.get('type'):
                    #                        reftable = f.get('type').split()[1]
                    for key in request.forms.keys():
                        if "data["+str(id)+"][" + f.get('name') + "][name]" in key:
                            print("if " + "data["+str(id)+"][" + f.get('name') + "][name]" + " in key")
                            print("True key:" + key)
                            try:
                                kwargs.update(
                                    {f.get('name'): int(request.forms.get("data["+str(id)+"][" + f.get('name') + "][name]"))})
                            except:
                                pass

                # Integers,
                elif ((f.get('type') == "blob") or (f.get('type') == "integer") or (f.get('type') == "double")
                      or (f.get('type') == "bigint") or ('decimal' in f.get('type'))):
                    #                       blob, integer, double, decimal(n, m), bigint
                    for key in request.forms.keys():
                        if "data["+str(id)+"][" + table._tablename + "][" + f.get('name') + "]" in key:
                            print("if " + "data["+str(id)+"][" + table._tablename + "][" + f.get('name') + "]" + " in key")
                            print("True key:" + key)
                            try:
                                kwargs.update({f.get('name'): int(
                                    request.forms.get("data["+str(id)+"][" + table._tablename + "][" + f.get('name') + "]"))})
                            except:
                                pass

                else:
                    # Stinrg, Text, password, json
                    for key in request.forms.keys():
                        if "data["+str(id)+"][" + table._tablename + "][" + f.get('name') + "]" in key:
                            print("STRING if " + "data["+str(id)+"][" + table._tablename + "][" + f.get('name') + "]" + " in key")
                            print("True key:" + key)
                            try:
                                kwargs.update({f.get('name'): request.forms.get(
                                    "data["+str(id)+"][" + table._tablename + "][" + f.get('name') + "]")})
                            except:
                                pass
            print("kwargs:" + str(kwargs) + "\r\r")

            """
            grower_id = request.forms.get("data["+str(id)+"][grower_id][name]")
            variety_id = request.forms.get("data["+str(id)+"][variety_id][name]")
            branch_id = request.forms.get("data["+str(id)+"][branch_id][name]")
            commencement_dt = datetime.strptime(request.forms.get("data["+str(id)+"][growercontract][commencement_dt]"), '%Y-%m-%d').date()
            expiry_dt = datetime.strptime(request.forms.get("data["+str(id)+"][growercontract][expiry_dt]"), '%Y-%m-%d').date()
            name = request.forms.get("data["+str(id)+"][growercontract][name]")
            contract_id = request.forms.get("data["+str(id)+"][growercontract][contract_id]")
            contractsigned = True if (request.forms.get("data["+str(id)+"][growercontract][contractsigned]")=="1") else False
            """

            gc_query = (table.id == id)
            z = db(gc_query).select().first()
            z.update_record(**kwargs)
            """
                name=name,
                grower_id=grower_id,
                variety_id=variety_id,
                branch_id=branch_id,
                commencement_dt=commencement_dt,
                contract_id=contract_id,
                expiry_dt=expiry_dt,
                contractsigned=contractsigned,
            )
            """
            db.commit()
            z = db(gc_query).select().first()

            data = [ generic_record_data(table,z) ]
            print("data: "+str(data))
            return json.dumps(dict(data=data), indent=4, sort_keys=True, default=str)
        elif action == "remove":
            id = 0
            for key in request.forms.keys():
                if "data" in key:
                    try:
                        a = key.split('[')
                        # print(str(a))
                        id = int(a[1].strip("]["))
                        print("id:" + str(id))
                        break
                    except:
                        return
        #   id = request.forms.get("growercontract")
            result = db(table.id == id).delete()
            print("result:"+str(result))
            return json.dumps(dict(data={}))
        elif action == "upload":
            """Handle file upload form"""
            upload = request.files.get('upload')
            print("upload: "+str(upload.filename)+' '+str(upload.name))
            # only allow upload of pdf files
            #if upload.content_type != 'application/pdf':#'text/plain':
             #   return "Only PDF files allowed"
            newid = db.upload.insert(
                name = '',
                filename = '',
                filesize = -1,
                web_path = '',
                system_path = '',
                table = str(table),
            )
            db.commit()
            print("newid:"+str(newid))

            upload.filename = table._tablename + '-' + str(newid) + right(upload.filename, 4)
            web_path = str(URL('downloadfile/'+ upload.filename))
            save_path = os.path.join(settings.UPLOAD_PATH,upload.filename)

            print("webpath:" + str(web_path))#os.path.join('downloadfile', upload.filename))))
            print("save_path:" + str(save_path))#os.path.join('downloadfile', upload.filename))))
            print("newid:" + str(newid))#os.path.join('downloadfile', upload.filename))))

            z = db(db.upload.id == newid).select(db.upload.ALL).first()
            print("z.id:" + str(z.id))#os.path.join('downloadfile', upload.filename))))
            ret = z.update_record(
                name = upload.filename,
                filename = upload.filename,
                filesize = upload.content_length,
                web_path = web_path,
                system_path = save_path,
                table=str(table),
            )
            db.commit()
            z = db(db.upload.id == newid).select(db.upload.ALL).first()
            print("newid:" + str(newid))#os.path.join('downloadfile', upload.filename))))
            print("com z.id:" + str(z.id))#os.path.join('downloadfile', upload.filename))))
            print("com z.filename:" + str(z.filename))#os.path.join('downloadfile', upload.filename))))
            print("com z.webpath:" + str(z.web_path))#os.path.join('downloadfile', upload.filename))))

            upload.save(save_path)
            #formulate the response:
            data = []

            files = {"uploadedfiles": {str(z.id): {
                "id": str(z.id),
                "filename": z.filename,
                "filesize": z.filesize,
                "web_path": z.web_path,
                "system_path": z.system_path,
                }
            }}
            upload = {"id": z.id,"filename":z.filename }
            return json.dumps(dict(data=data, files=files, upload=upload), indent=4, sort_keys=True, default=str)


    else:
        return json.dumps(dict(data={}), indent=4, sort_keys=True, default=str)

