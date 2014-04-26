###November 2006: Posted by Kevin Walzer, kw@codebykevin.com. Based on Tablelist wrapper by Martin Franklin. 
###Freely reusable.

###December 2007: Minor update to add keyboard navigation/TablelistSelect virutal event to demo.--KW

import os
import sys

if sys.version_info[0] == 3:
    from tkinter import *
else:
    from Tkinter import *

class TableList(Widget):
    '''A tablelist widget is a multi-column listbox.  
    
    The width of each column can be dynamic (i.e., just large enough to hold all its elements, 
    including the header) or static (specified in characters or pixels).  The columns are, per
    default, resizable.  The alignment of each column can be specified as left, right, or center.
    
    The columns, rows, and cells can be configured individually.  Several of the global and 
    column-specific options refer to the headers, implemented as label widgets.  For instance, 
    the -labelcommand option specifies a Tcl command to be invoked when mouse button 1 is released over
    a label.  The most common value of this option is tablelist::sortByColumn, which sorts the items 
    based on the respective column.
    
    Interactive editing of the elements of a tablelist widget can be enabled for individual cells and 
    for entire columns.  A great variety of widgets from the Tk core and from the packages BWidget, 
    Iwidgets, combobox, and Mentry is supported for being used as embedded edit window.  In addition, 
    a rich set of keyboard bindings is provided for a comfortable navigation between the editable cells.
    
    The Tcl command corresponding to a tablelist widget is very similar to the one associated with a 
    normal listbox.  There are column-, row-, and cell-specific counterparts of the configure and cget 
    subcommands (columnconfigure, rowconfigure, cellconfigure, ...).  They can be used, among others, 
    to insert images into the cells and the header labels, or to insert embedded windows into the cells.  
    The index, nearest, and see command options refer to the rows, but similar subcommands are provided
    for the columns and cells (columnindex, cellindex, ...).  The items can be sorted with the sort and
    sortbycolumn command options.
    
    The bindings defined for the body of a tablelist widget make it behave just like a normal listbox.
    This includes the support for the virtual event <<ListboxSelect>> 
    (which is equivalent to <<TablelistSelect>>).  In addition, version 2.3 or higher of the widget 
    callback package Wcb (written in pure Tcl/Tk code as well) can be used to define callbacks for the 
    activate,  selection set,  and  selection clear  commands, and Wcb version 3.0 or higher also 
    supports callbacks for the activatecell,  cellselection set,  and  cellselection clear  commands.  
    The download location of Wcb is

    http://www.nemethi.de 
    '''     
    def __init__(self, master=None, cnf={}, **kw):
        _loadtablelist(master)
        Widget.__init__(self, master, 'tablelist::tablelist', cnf, kw)
        
        
## my methods.....

    def getcurselection(self):
        """return list of currently selected items (as a list of lists)"""
        selection = self.curselection()
        selected = []
        for s in selection:
            selected.append(self.get(s))
        return selected

    def setlist(self, data):
        """clear the list and add the rows from the data"""
        self.clear()
        for row in data:
            self.insert("end", row)


    def clear(self):
        """delete all items from the tablelist"""
        self.tk.call((self._w, "delete", 0, "end"))
        
    def body_bind(self, sequence, func, add=None):
        """Bind sequence to function on tablelist BODY
        """
        return self._bind(('bind', self.bodytag()), sequence, func, add)
    # commented this out because this bind doesn't work with it
    # tablelist.bind('<<TablelistRowMoved>>', some_callback)
    #bind = body_bind

## TableList methods

    def activate(self, index):
        """Sets the active item to the one indicated by index if the 
        tablelist"s state is not disabled.  
        
        If index  is outside the range  of items in the tablelist then 
        the closest item is activated.  The active item is drawn as 
        specified by the -activestyle  configuration option when the 
        widget has the input focus and the selection type is row.  Its 
        index may be retrieved with the index active.  Returns an empty
        string.
        """
        return self.tk.call((self._w, "activate", index))
        
    def activatecell(self, index):
        """Sets the active element to the one indicated by cellIndex 
        if the tablelist"s state is not disabled.  
        
        If cellIndex is outside the range of elements in the tablelist 
        or it refers to a hidden element, then the closest non-hidden 
        element is activated.  The active element is drawn as specified
        by the -activestyle configuration option when the widget has the
        input focus and the selection type is cell.  Its index may be 
        retrieved with the cell index active.  Returns an empty string.
        """
        return self.tk.call((self._w, "activatecell", index))
        
    def attrib(self, cnf={}, **kw):
        """Queries or modifies the attributes of the widget.  
        
        If no name is specified, the command returns a list of pairs, 
        each of which contains the name and the value of an attribute 
        for pathName.  If name is specified with no value, then the 
        command returns the value of the one named attribute.  If one 
        or more name-value pairs are specified, then the command sets 
        the given widget attribute(s) to the given value(s); in this 
        case the return value is an empty string.  name may be an 
        arbitrary string.
        """
        return self.tk.call((self._w, "attrib") +
                     self._options(cnf, kw))
        
    def bbox(self, *args):
        """Returns a list of four numbers describing the bounding box
        of the row given by index.  
        
        The first two elements of the list give the x and y coordinates
        of the upper-left corner of the screen area covered by the row 
        (specified in pixels relative to the widget) and the last two 
        elements give the width and height of the area, in pixels.  If 
        no part of the row given by index is visible on the screen, or 
        if index refers to a non-existent row, then the result is an 
        empty string; if the row is partially visible, the result gives
        the full area of the row, including any parts that are not 
        visible. 
        """
        return self._getints(
            self.tk.call((self._w, "bbox") + args)) or None



    def bodypath(self):
        """Returns the path name of the body component of the widget.
        """
        return self.tk.call((self._w, "bodypath"))
        
    def bodytag(self):
        """Returns the name of a binding tag whose name depends on the 
        path name of the tablelist widget and which is associated with
        the tablelist"s body, the separator frames, and the labels used 
        for displaying embedded images.  This binding tag is designed 
        to be used when defining individual binding scripts for 
        tablelist widgets.  The main advantage of using this tag 
        instead of the path name of the tablelist"s body is that it 
        enables you to write event handling scripts that are valid not 
        only for the tablelist"s body but also for the separators and 
        embedded images.  This binding tag precedes the tag 
        TablelistBody in the list of binding tags of the tablelist 
        descendants mentioned above.
        """
        return self.tk.call((self._w, "bodytag"))
        
        
    def cancelediting(self):
        """This subcommand cancels the interactive editing of the 
        contents of the cell whose index was passed to the editcell 
        subcommand, destroys the temporary widget embedded into the 
        cell, and restores the original cell contents.  This command 
        enables you to cancel the interactive cell editing from within 
        the Tcl command specified by the -editstartcommand  
        configuration option if that pre-edit callback encounters an 
        error when preparing the text to be inserted into the edit 
        window.  The command is also invoked implicitly by pressing 
        the Escape key when a cell is being edited.  The return value 
        is an empty string, which is also returned if no cell was 
        being edited when the command was invoked.
        """
        return self.tk.call((self._w, "cancelediting"))
        
    def cellcget(self, index, option):
        """Returns the current value of the cell configuration option 
        given by option for the cell specified by cellIndex.  option  
        may have any of the values accepted by the cellconfigure 
        command.
        """
        return self.tk.call((self._w, "cellcget", index, option))
        
    def cellconfigure(self, index, cnf={}, **kw):
        """Queries or modifies the configuration options of the cell 
        given by cellIndex.  If no option is specified, the command 
        returns a list describing all of the available options for 
        the cell (see Tk_ConfigureInfo for information on the format 
        of this list).  If option is specified with no value, then 
        the command returns a list describing the one named option 
        (this list will be identical to the corresponding sublist of 
        the value returned if no option is specified).  If one or 
        more option-value pairs are specified, then the command 
        modifies the given cell option(s) to have the given 
        value(s); in this case the return value is an empty string.  
        option may have any of the following
        
        
        CELL CONFIGURATION OPTIONS
        
        The following options are currently supported by the cellcget
        and cellconfigure commands:
        
        -background color or -bg color
            Specifies the normal background color to use when displaying
            the contents of the cell.
    
        -editable boolean
            Specifies whether the contents of the cell can be edited 
            interactively.  The default value is 0.  This option 
            overrides the one with the same name for the column 
            containing the given cell.
    
        -font font
            Specifies the font to use when displaying the contents
            of the cell.
    
        -foreground color or -fg color
            Specifies the normal foreground color to use when 
            displaying the contents of the cell.
    
        -image image
            Specifies the name of the Tk image to be displayed in the
            cell.  image must be the result of an invocation of the  
            image create  command, or an empty string, specifying that
            no image is to be displayed.  If the column containing the 
            cell is right-aligned then the image will be displayed to 
            the right of the cell"s text, otherwise to its left.  The 
            text and the image are separated from each other by a 
            space character.  If for the same cell the -window option 
            was specified with a nonempty value then it overrides the 
            -image option.  If the tablelist"s state is disabled then 
            this option will be ignored.
            
            To display an image in a cell, Tablelist makes use of an 
            embedded label widget.  This requires more memory than 
            inserting the image directly into the tablelist"s body, but
            has the main advantage of making it possible to adjust the 
            width of the label containing the widget to fit into its 
            column.  This has the visual effect of cutting off part of 
            the image from its right or left side, depending on the 
            column"s alignment.&nbspM; To make sure that images with 
            transparent background will be dispklayed correctly, the 
            background color of the label widgets containing the 
            embedded images is automatically updated whenever necessary.
        
        -selectbackground color
            Specifies the background color to use when displaying the 
            contents of the cell while it is selected.
            
        -selectforeground color
            Specifies the foreground color to use when displaying the 
            contents of the cell while it is selected.
            
        -text text
            Specifies the string to be displayed in the given cell, 
            i.e., updates the element contained in the cell.  If the 
            tablelist"s state is disabled then this option will be 
            ignored.
            
        -window command
            Specifies a Tcl command creating the window to be embedded
            into the cell.  The command is automatically concatenated 
            with the name of the tablelist widget, the cell"s row and 
            column indices, as well as the path name of the embedded 
            window to be created, and the resulting script is evaluated
            in the global scope.  command may also be an empty string, 
            specifying that no embedded window is to be displayed.  If 
            the column containing the cell is right-aligned then the 
            window will be displayed to the right of the cell"s text, 
            otherwise to its left.  The text and the window are 
            separated from each other by a space character.  If this 
            option was specified with a nonempty value then it 
            overrides the -image cell configuration option.  If the 
            tablelist"s state is disabled then this option will be 
            ignored.
            
            There are several situations where the embedded window will 
            be destroyed and later recreated by invoking the script 
            mentioned above.  For example, when changing the value of 
            some of the tablelist widget or column configuration 
            options, sorting the items, or moving a row or a column,
            the widget"s contents will be redisplayed, which makes it 
            necessary to recreate the embedded windows.  This operation
            won"t preserve the changes made on the embedded windows 
            after their creation.  For this reason, you should avoid 
            any changes on embedded windows outside their creation 
            scripts.
            
        The -background, -font, -foreground, -selectbackground, and 
        -selectforeground cell configuration options override the 
        options with the same names set at row, column, or widget level
        if the specified value is not an empty string.  
        
        See the COLORS AND FONTS section for further details on these options.
        
        """
        self.tk.call((self._w, "cellconfigure", index) +
                     self._options(cnf, kw))
        
    def cellindex(self, index):
        """Returns the canonical cell index value that corresponds to 
        cellIndex, in the form row,col, where row and col are integers.
        """
        return self.tk.call((self._w, "cellindex", index))
        
    def cellselection_anchor(self, index):
        """Sets the cell selection anchor to the element given by 
        cellIndex.  
        
        If cellIndex refers to a nonexistent or hidden element, then 
        the closest non-hidden element is used.  The cell selection 
        anchor is the end of the cell selection that is fixed while
        dragging out a cell selection with the mouse if the selection 
        type is cell.  The cell index anchor may be used to refer to 
        the anchor element.
        """
        self.tk.call((self._w, "cellselection", "anchor", index))
        
        
    def cellselection_clear(self, first, last=None):
        """If any of the elements between firstCell and lastCell 
        (inclusive) or corresponding to the cell indices specified
        by the list cellIndexList are selected, they are deselected.  
        The selection state is not changed for elements outside the 
        range given in the first form of the command or different 
        from those specified by the cell index list given in its 
        second form.
        """
        return self.tk.call(
            self._w, "cellselection", "clear", first, last)
            

    def cellselection_includes(self, index):
        """Returns 1 if the element indicated by cellIndex is 
        currently selected, 0 if it isn't
        """
        return self.tk.call((self._w, "cellselection", "includes", index))

    def cellselection_set(self, first, last=None):
        """Selects all of the selectable elements in the range between 
        firstCell and lastCell, inclusive, or corresponding to the 
        indices specified by the list cellIndexList, without affecting 
        the selection state of any other elements.  An element is viewed 
        as selectable if and only if the value of the -selectable option
        of the row containing it is true.
        """
        return self.tk.call(
            self._w, "cellselection", "set", first, last)
            
        
    def cget(self, option):
        """Returns the current value of the configuration option given 
        by option, which may have any of the values accepted by the 
        tablelist::tablelist command.
        """
        return self.tk.call((self._w, "cget", option))
    
    def columncget(self, index, option):
        """Returns the current value of the column configuration option 
        given by option for the column specified by columnIndex.  option 
        may have any of the values accepted by the columnconfigure 
        command.
        """
        return self.tk.call((self._w, "columnget", index, option))
    
    def columnconfigure(self, index, cnf={}, **kw):
        """Queries or modifies the configuration options of the column 
        given by columnIndex.  
        
        If no option is specified, the command returns a list describing 
        all of the available options for the column (see Tk_ConfigureInfo 
        for information on the format of this list).  If option is 
        specified with no value, then the command returns a list 
        describing the one named option (this list will be identical 
        to the corresponding sublist of the value returned if no option 
        is specified).  If one or more option-value pairs are specified, 
        then the command modifies the given column option(s) to have the 
        given value(s); in this case the return value is an empty string.  
        option may have any of the values described in the 
        COLUMN CONFIGURATION OPTIONS section.
        """
        return self.tk.call((self._w, "columnconfigure", index) +
                     self._options(cnf, kw))
        
    
    def columncount(self):
        """Returns the number of columns in the tablelist widget."""
        return self.tk.call((self._w, "columncount"))
    
    def columnindex(self, index):
        """Returns the integer column index value that corresponds 
        index.        
        """
        return self.tk.call((self._w, "columnindex", index))
        
    def configure(self, cnf={}, **kw):
        """Queries or modifies the configuration options of the 
        widget.  
        
        If no option is specified, the command returns a list 
        describing all of the available options for def (see 
        Tk_ConfigureInfo for information on the format of this list).  
        If option is specified with no value, then the command 
        returns a list describing the one named option (this list 
        will be identical to the corresponding sublist of the value 
        returned if no option is specified).  If one or more 
        option-value pairs are specified, then the command modifies
        the given widget option(s) to have the given value(s); in 
        this case the return value is an empty string.  option may 
        have any of the values accepted by the tablelist::tablelist 
        command.
        """
        return self.tk.call((self._w, "configure") +
                     self._options(cnf, kw))
    config = configure

        
    def containing(self, y):
        """Given a y-coordinate within the tablelist window
        this command returns the index of the tablelist item containing 
        that y-coordinate.  If no corresponding item is found then the 
        return value is -1.  The coordinate y is expected to be relative
        to the tablelist window itself (not its body component).
        """
        return self.tk.call((self._w, "containing", y))

    def containingcell(self, x, y):
        """Given an x- and a y-coordinate within the tablelist window, 
        this command returns the index of the tablelist cell containing 
        the point having these coordinates.  If no corresponding cell is
        found then the row or column component (or both) of the return 
        value is -1.  The coordinates x and y are expected to be relative
        to the tablelist window itself (not its body component).
        """
        return self.tk.call((self._w, "containingcell", x, y))

    def containingcolumn(self, x):
        """Given an x-coordinate within the tablelist window, 
        this command returns the index of the tablelist column 
        containing that x-coordinate.  If no corresponding column
        is found then the return value is -1.  The coordinate x is 
        expected to be relative to the tablelist window itself 
        (not its body component).
        """
        return self.tk.call((self._w, "containingcolumn", x))


    def curcellselection(self):
        """Returns a list containing the canonical indices 
        (of the form row,col, where row and col are numbers) of 
        all of the non-hidden elements in the tablelist that are 
        currently selected.  If there are no such elements in the
        tablelist then an empty string is returned.
        """
        return self.tk.call((self._w, "curcellselection"))

    def curselection(self):
        """Returns a list containing the numerical indices of 
        all of the items in the tablelist that contain at least 
        one non-hidden selected element.  If there are no such 
        items in the tablelist then an empty string is returned.
        """
        return self.tk.splitlist(self.tk.call((self._w, "curselection")))

    def delete(self, first, last=None):
        """Deletes one or more items of the tablelist if its 
        state is not disabled.  In the first form of the command, 
        first and last are indices specifying the first and last 
        items in the range to delete.  The command's second form 
        accepts a list indexList of indices specifying the items 
        to be deleted.  Returns an empty string.
        """
        if last:
            return self.tk.call(self._w, "delete", first, last)
        else:
            return self.tk.call(self._w, "delete", first)
            

    def deletecolumns(self, first, last=None):
        """Deletes one or more columns of the tablelist if its 
        state is not disabled.  In the first form of the command, 
        firstColumn and lastColumn are indices specifying the 
        first and last columns in the range to delete.  The 
        command's second form accepts a list columnIndexList of 
        indices specifying the columns to be deleted.  
        Returns an empty string.
        """
        if last:
            return self.tk.call(self._w, "deletecolumns", first, last)
        else:
            return self.tk.call(self._w, "deletecolumns", first)
            

    def editcell(self, index):
        """Starts the interactive editing of the cell's contents 
        if the tablelist's state is not disabled, the cell's column
        is not hidden, and the cell is editable.  Returns an empty 
        string.  See the INTERACTIVE CELL EDITING section for 
        details on editablity and on the editing process.
        """
        return self.tk.call((self._w, "editcell", index))

    def editwinpath(self):
        """Returns the path name of the temporary embedded widget 
        used for interactive cell editing, created by the editcell 
        subcommand.  If no cell is currently being edited then the 
        return value is an empty string.  This subcommand enables 
        you to access the edit window from within the commands 
        specified by the -editstartcommand and -editendcommand 
        configuration options.
        """
        return self.tk.call((self._w, "editwinpath"))

    def entrypath(self):
        """Returns the path name of the entry or entry-like 
        component of the temporary embedded widget used for 
        interactive cell editing, created by the editcell 
        subcommand.  If no cell is currently being edited or 
        the editing is taking place with the aid of a checkbutton 
        or mentry widget then the return value is an empty string; 
        otherwise it is the path name of an entry, spinbox, or 
        BWidget Entry widget, which can be the edit window itself 
        or one of its descendants.  This subcommand enables you 
        to access the entry or entry-like component of the 
        temporary embedded widget from within the commands 
        specified by the -editstartcommand and -editendcommand 
        configuration options.
        """
        return self.tk.call((self._w, "entrypath"))

    def fillcolumn(self, index, text):
        """Sets all the elements of the specified column to the value text."""
        return self.tk.call((self._w, "fillcolumn", index, text))

    def finishediting(self):
        """This subcommand attempts to terminate the interactive editing 
        of the contents of the cell whose index was passed to the editcell
        subcommand by destroying the temporary widget embedded into the 
        cell and updating the cell's contents.  The exact steps involved 
        are as follows:  First, the widget's final text is compared to 
        its original one.  If they are equal then the edit window is 
        destroyed and the cell's original contents are restored.  If the 
        two strings are different and the value of the -editendcommand 
        configuration option is a nonempty string, then the widget's final 
        text is passed to that command as its last argument (following the
        tablelist's path name as well as the cell's row and column 
        indices), the resulting script is evaluated in the global scope, 
        and the return value becomes the cell's new contents after 
        destroying the edit window.  However, if from within this script
        the rejectinput subcommand was invoked then the cell's value is
        not changed and the embedded widget remains displayed in the cell;
        in this case the command returns the boolean value 0.  In all the 
        other cases, the return value is 1; the latter is also returned if
        no cell was being edited when the command was invoked.  Before 
        returning the value 1, the command generates the virtual event 
        <<TablelistCellUpdated>> if the cell's text was changed.  This 
        subcommand is called implicitly by pressing Return or KP_Enter 
        when editing a cell, or by clicking with the left mouse button 
        anywhere in the tablelist's body, outside the cell just being 
        edited, or moving into another editable cell by using keyboard 
        navigation.
        """
        return self.tk.call((self._w, "finishediting"))
        
    def get(self, first, last=None):
        """The first form of the command returns a list whose elements 
        are all of the tablelist items between first and last, inclusive.  
        The value returned by the second form depends on the number of 
        elements in the list indexList: if the latter contains exactly one 
        index then the return value is the tablelist item indicated by that
        index (or an empty string if the index refers to a non-existent 
        item); otherwise the command returns the list of all of the 
        tablelist items corresponding to the indices specified by indexList.
        """
        if last:
            data = []
            for row in self.tk.splitlist(self.tk.call(self._w, "get", first, last)):
                data.append(self.tk.splitlist(row))
            return data
        else:
            return self.tk.splitlist(
                self.tk.call(self._w, "get", first))

    def getcolumns(self, first, last=None):
        """The first form of the command returns a list whose elements 
        are lists themselves, where each of the sublists corresponds to 
        exactly one column between firstColumn and lastColumn, inclusive, 
        and consists of all of the tablelist elements contained in that 
        column.  The value returned by the second form depends on the 
        number of elements in the list columnIndexList: if the latter 
        contains exactly one column index then the return value is a list 
        consisting of all of the tablelist elements contained in the 
        column indicated by that column index; otherwise the command 
        returns a list whose elements are lists themselves, where each of
        the sublists corresponds to exactly one column index in 
        columnIndexList and consists of all of the tablelist elements 
        contained in that column.
        """
        if last:
            return self.tk.splitlist(self.tk.call(
                self._w, "getcolumns", first, last))
        else:
            return self.tk.call(self._w, "getcolumns", first)
            
        
    def getkeys(self, first, last=None):
        """The first form of the command returns a list whose elements 
        are all of the sequence numbers associated with the tablelist 
        items between first and last, inclusive.  The value returned by 
        the second form depends on the number of elements in the list 
        indexList: if the latter contains exactly one index then the 
        return value is the sequence number associated with the tablelist
        item indicated by that index (or an empty string if the index 
        refers to a non-existent item); otherwise the command returns 
        the list of all of the sequence numbers associated with the 
        tablelist items corresponding to the indices specified by 
        indexList.  Each item of a tablelist widget has a unique sequence
        number that remains unchanged until the item is deleted, thus 
        acting as a key that uniquely identifies the item even if the 
        latter's position (i.e., row index) changes.  This command 
        provides read-only access to these internal item IDs.
        """
        if last:
            return self.tk.splitlist(self.tk.call(
                self._w, "getkeys", first, last))
        else:
            return self.tk.call(self._w, "getkeys", first)
            

    def index(self, index):
        """Returns the integer row index value that corresponds to index.  
        
        If index is end then the return value is the number of items in 
        the tablelist (not the index of the last item).
        """
        return self.tk.call((self._w, "index", index))

    def insert(self, index, *items):
        """Inserts zero or more new items in the widget's internal list 
        just before the item given by index if the tablelist's state is not
        disabled.  If index equals the number of items or is specified as 
        end then the new items are added to the end of the widget's list.  
        Tabulator and newline characters are displayed as \t and \n (i.e.,
        a backslash followed by a t and n, respectively), but are inserted
        unchanged into the internal list.  The return value is an empty 
        string.
        """
        return self.tk.call((self._w, "insert", index) + items)

    def insertcolumnlist(self, index, list):
        """Inserts the columns specified by the list columnList just before
        the column given by columnIndex if the tablelist's state is not 
        disabled.  If columnIndex equals the number of columns or is 
        specified as end then the new columns are added to the end of the 
        column list.  The argument columnList must be a list containing the
        width, title, and optional alignment specifications for the new 
        columns, in the same form as in the case of the -columns 
        configuration option.  The return value is an empty string.  
        The elements of the new columns are initially empty strings; the 
        easiest way to change these values is to use the fillcolumn 
        subcommand or the -text column configuration option.  
        """
        return self.tk.call((self._w, "insertcolumnlist", index) + list)


    def insertcolumns(self, index, *columns):
        """Inserts zero or more new columns just before the column given 
        by index if the tablelist's state is not disabled.  If columnIndex
        equals the number of columns or is specified as end then the new 
        columns are added to the end of the column list.  The arguments 
        following the column index have the same meanings as in the case 
        of the -columns configuration option.  The return value is an 
        empty string.  The elements of the new columns are initially 
        empty strings; the easiest way to change these values is to use 
        the fillcolumn subcommand or the -text column configuration option.
        """
        return self.tk.call((self._w, "insertcolumns", index) + columns)
        

    def insertlist(self, index, *items):
        """Inserts the items of the list itemList in the widget's internal 
        list just before the item given by index if the tablelist's state 
        is not disabled.  If index equals the number of items or is 
        specified as end then the new items are added to the end of the 
        widget's list.  Tabulator and newline characters are displayed 
        as \t and \n (i.e., a backslash followed by a t and n, 
        respectively), but are inserted unchanged into the internal list. 
        The return value is an empty string.  
        """
        return self.tk.call((self._w, "insertlist", index) + items)
       
    def itemlistvar(self):
        """Returns the name of a variable used by Tablelist to hold the 
        widget's internal list.  The recommended way to use this variable 
        is to create a link to it with the aid of the upvar command, 
        like in the following example:

            upvar #0 [.tbl itemlistvar] itemList 

        In this example, the value of the variable itemList will be the 
        internal list of the tablelist widget .tbl.  Each element of the
        widget's internal list corresponds to one item, and it is in turn
        a list whose elements correspond to the elements of that item, 
        except that it has one additional element, holding the item's key.

        The itemlistvar command provides an efficient way of accessing 
        this internal list, instead of retrieving the items with the get 
        subcommand or using the -listvariable option (these methods consume
        significantly more memory).  It can be useful in situations where 
        the elements of a tablelist widget are to be accessed for creating
        text files, HTML output, XML data, database commands, etc.  This 
        should, however, be a strictly readonly access; otherwise the 
        results will be unpredictable!
        """
        return self.tk.call((self._w, "itemlistvar"))

    def labelpath(self, index):
        """Returns the path name of the header label corresponding to the
        column indicated by columnIndex.
        """
        return self.tk.call((self._w, "labelpath", index))

    def labels(self):
        """Returns a list containing the path names of all header labels 
        of the widget.
        """
        return self.tk.call((self._w, "labels"))

    def move(self, src, dst):
        """Moves the item indicated by src just before the one given by 
        dst if the tablelist's state is not disabled.  If target equals
        the nunber of items or is specified as end then the source item
        is moved after the last one.  Returns an empty string.
        """
        return self.tk.call((self._w, "move", src, dst))

    def movecolumn(self, src, dst):
        """Moves the column indicated by src just before the one given 
        by dst if the tablelist's state is not disabled.  If dst equals
        the number of columns or is specified as end then the source 
        column is moved after the last one.  Returns an empty string.
        """
        return self.tk.call((self._w, "movecolumn", src, dst))

    def nearest(self, y):
        """Given a y-coordinate within the tablelist window, this command
        returns the index of the tablelist item nearest to that
        y-coordinate.  The coordinate y is expected to be relative to the 
        tablelist window itself (not its body component).
        """
        return getint(self.tk.call((self._w, "nearest", y)))+1

    def nearestcell(self, x, y):
        """Given an x- and a y-coordinate within the tablelist window,
        this command returns the index of the non-hidden tablelist cell 
        nearest to the point having these coordinates.  The coordinates x 
        and y are expected to be relative to the tablelist window itself 
        (not its body component).
        """
        return self.tk.call((self._w, "nearestcell", x, y))


    def nearestcolumn(self, x):
        """Given an x-coordinate within the tablelist window, this command
        returns the index of the non-hidden tablelist column nearest to 
        that x-coordinate.  The coordinate x is expected to be relative to 
        the tablelist window itself (not its body component).
        """
        return self.tk.call((self._w, "nearestcolumn", x))


    def rejectinput(self):
        """If invoked from within the Tcl command specified by the 
        -editendcommand configuration option, then this subcommand prevents 
        the termination of the interactive editing of the contents of the 
        cell whose index was passed to the editcell subcommand.  It invokes
        the seecell subcommand to make sure the respective cell becomes 
        visible (in case it was scrolled out of view), and sets the focus 
        to the temporary widget embedded into the cell.  This command 
        enables you to reject the widget's text during the final validation
        of the string intended to become the new cell contents.
        """
        return self.tk.call((self._w, "rejectinput"))


    def resetsortinfo(self):
        """Resets the information about the sorting of the items.  
        Subsequent invocations of sortcolumn and sortorder will return
        -1 and an empty string, respectively.  This command also removes
        an existing up- or down-arrow displayed in any of the header 
        labels by an earlier invocation of sortbycolumn.  The return 
        value is an empty string.
        """
        return self.tk.call((self._w, "resetsortinfo"))


    def rowcget(self, index, option):
        """Returns the current value of the row configuration option 
        given by option for the row specified by index.  option may have
        any of the values accepted by the rowconfigure command.
        """
        return self.tk.call((self._w, "rowcget", index, option))


    def rowconfigure(self, index, cnf={}, **kw):
        """Queries or modifies the configuration options of the row given
        by index.  If no option is specified, the command returns a list 
        describing all of the available options for the row (see 
        Tk_ConfigureInfo for information on the format of this list). 
        If option is specified with no value, then the command returns a 
        list describing the one named option (this list will be identical
        to the corresponding sublist of the value returned if no option 
        is specified).  If one or more option-value pairs are specified, 
        then the command modifies the given row option(s) to have the given
        value(s); in this case the return value is an empty string.  option
        may have any of the values described in the 
        ROW CONFIGURATION OPTIONS section.
        """
        return self.tk.call((self._w, "rowconfigure", index) +
                     self._options(cnf, kw))
    def scan_mark(self, x, y):
        """Remember the current X, Y coordinates."""
        self.tk.call(self._w, "scan", "mark", x, y)
        
    def scan_dragto(self, x, y):
        """Adjust the view of the listbox to 10 times the
        difference between X and Y and the coordinates given in
        scan_mark."""
        self.tk.call(self._w, "scan", "dragto", x, y)
        
    def see(self, index):
        """Scroll such that INDEX is visible."""
        self.tk.call(self._w, "see", index)
        
    def seecell(self, index):
        """Adjusts the view in the tablelist so that the cell given by 
        index is visible.  If the cell is already visible then the command 
        has no effect; if the cell is near one edge of the window then the 
        tablelist scrolls to bring the cell into view at the edge; otherwise
        the tablelist scrolls to center the cell.  If the value of the 
        -titlecolumns option is positive then the centering of the cell is 
        only done vertically; the horizontal scrolling (which in this case 
        is performed column-wise) will just bring the cell into view next 
        to the title columns or at the right edge of the window.
        """
        self.tk.call(self._w, "seecell", index)
        
    def seecolumn(self, index):
        """Adjusts the view in the tablelist so that the column given by 
        index is visible.  If the column is already visible then the command
        has no effect; if the column is near one edge of the window then the
        tablelist scrolls horizontally to bring the column into view at the 
        edge; otherwise the tablelist scrolls horizontally to center the 
        column.  If the value of the -titlecolumns option is positive then
        the horizontal scrolling (which in this case is performed column-wise)
        will just bring the column into view next to the title columns or at
        the right edge of the window.
        """
        self.tk.call(self._w, "seecolumn", index)
        
    def selection_anchor(self, index):
        """Set the fixed end oft the selection to INDEX."""
        self.tk.call(self._w, "selection", "anchor", index)
    select_anchor = selection_anchor
    
    def selection_clear(self, first, last=None):
        """Clear the selection from FIRST to LAST (not included)."""
        self.tk.call(self._w,
                 "selection", "clear", first, last)
    select_clear = selection_clear
    
    def selection_includes(self, index):
        """Return 1 if INDEX is part of the selection."""
        return self.tk.getboolean(self.tk.call(
            self._w, "selection", "includes", index))
    select_includes = selection_includes
    
    def selection_set(self, first, last=None):
        """Set the selection from FIRST to LAST (not included) without
        changing the currently selected elements."""
        self.tk.call(self._w, "selection", "set", first, last)
    select_set = selection_set
        


    def separatorpath(self, index=None):
        """If the optional argument is not specified, then this 
        command returns the path name of the special separator 
        frame displayed to mark the end of the title columns if 
        the value of the -titlecolumns option is positive and an 
        empty string otherwise.  If the optional argument is present,
        then the command returns the path name of the separator 
        frame attached to the right edge of the header label indicated 
        by columnIndex if the value of the -showseparators configuration
        option is true and an empty string otherwise.
        """
        return self.tk.call(self._w, "separatorpath", index)


    def separators(self):
        """Returns a list containing the path names of all column 
        separators.  If the value of the -titlecolumns option is 
        positive then the first element of the list will be the path
        name of the special separator frame displayed to mark the 
        end of the title columns.  Whether the path names of the other 
        separators are included in the list, depends on the value of
        the -showseparators configuration option.
        """
        return self.tk.call(self._w, "separators")

    def size(self):
        """Return the number of elements in the tablelist."""
        return self.tk.call(self._w, "size")
        
    def sort(self, order="increase"):
        """Sorts the items in increasing or decreasing order, as specified 
        by the optional argument.  The default is -increasing.  Uses the 
        value of the -sortcommand widget configuration option as comparison
        command.  sort also removes an existing up- or down-arrow displayed
        in any of the header labels by an earlier invocation of the 
        sortbycolumn command.
        """
        return self.tk.call(self._w, "sort", order)
        

    def sortbycolumn(self, index, order=""):
        """Sorts the items based on the elements of the column given by index
        in increasing or decreasing order, as specified by the optional argument
        The default is -increasing.  The sorting process is controlled by the 
        values of the -sortmode and -sortcommand options for the given column.
        If both the value of the -showarrow configuration option and that of 
        the -showarrow option for the specified column are true then an up- or 
        down-arrow indicating the sorting order will be placed into the 
        column's label.  The shape of the arrow depends on the command's 
        optional argument and on the value of the -incrarrowtype configuration
        option.  If the label's contents are right-aligned then the arrow will
        be displayed on the left side of the label, otherwise on its right side.
        """
        return self.tk.call(self._w, "sortbycolumn", index, order)


    def sortcolumn(self):
        """Returns the numerical index of the column by which the 
        items were last sorted with the aid of the sortbycolumn 
        command, or -1 if they were last sorted with the sort 
        command or haven't been sorted at all, or the sorting 
        information was reset by invoking resetsortinfo.
        """
        return self.tk.call(self._w, "sortcolumn")

    def sortorder(self):
        """Returns the sorting order (as increasing or decreasing) from 
        the last invocation of the sort or sortbycolumn command, or an 
        empty string if the items haven't been sorted at all, or the 
        sorting information was reset by invoking resetsortinfo.
        """
        return self.tk.call(self._w, "sortorder")


    def xview(self, *what):
        """Query and change horizontal position of the view."""
        if not what:
            return self._getdoubles(self.tk.call(self._w, 'xview'))
        self.tk.call((self._w, 'xview') + what)
        
    def xview_moveto(self, fraction):
        """Adjust the view in the window so that FRACTION of the
        total width of the entry is off-screen to the left."""
        self.tk.call(self._w, 'xview', 'moveto', fraction)
        
    def xview_scroll(self, number, what):
        """Shift the x-view according to NUMBER which is measured in "units" or "pages" (WHAT)."""
        self.tk.call(self._w, 'xview', 'scroll', number, what)
        
    def yview(self, *what):
        """Query and change vertical position of the view."""
        if not what:
            return self._getdoubles(self.tk.call(self._w, 'yview'))
        self.tk.call((self._w, 'yview') + what)
        
    def yview_moveto(self, fraction):
        """Adjust the view in the window so that FRACTION of the
        total width of the entry is off-screen to the top."""
        self.tk.call(self._w, 'yview', 'moveto', fraction)
        
    def yview_scroll(self, number, what):
        """Shift the y-view according to NUMBER which is measured in "units" or "pages" (WHAT)."""
        self.tk.call(self._w, 'yview', 'scroll', number, what)


class ScrolledTableList(Frame):
    def __init__(self, parent, **kw):
        Frame.__init__(self, parent)
        self.tablelist = TableList(self, **kw)
        self.tablelist.pack(side="left", expand="yes", fill="both")
        self.vbar = Scrollbar(self, name='vbar')
        self.vbar.pack(side="right", fill="y")
        self.tablelist['yscrollcommand'] = self.vbar.set
        self.vbar['command'] = self.tablelist.yview
        
        ## forward the tablelist methods to myself (Frame)
        methods = TableList.__dict__.keys()
        for m in methods:
            setattr(self, m, getattr(self.tablelist, m))

        
def _loadtablelist(parent, path=None):
    """try loading the tablelist into the tkinter core
    
    parent is Tkinter parent widget instance (container)
    
    path is the location of the tablelist.tcl file
    if None the I will assume it's in the same directory 
    as this file
    """
    if not path:
        try:
            ## i'm imported
            path = os.path.split(os.path.abspath(__file__))[0]
        except:
            ## i'm running
            path = os.path.abspath(sys.path[0])
    # auto_path adds the tablelist tcl package to the tk / tcl search path (in python speak)
    parent.tk.call("lappend", "auto_path", path)    
    # register tablelist with tkinter
    parent.tk.call("package", "require", "tablelist")




#~ extensive ;-) test suite follows:
#~
#~

def tabletest():
    """quick test 
    
    Selection mode is default (row)
    no cells are editable
    table is sorted by clicking on column labels
    """
        
    root = Tk()
    root.title("TableList Test #1")
    
    tl = TableList(root, 
        background = "white",
        columns = (0, "First", 0, "Second", 0, "Third"),
        stretch = "all",
        width = 50,
        setfocus = 1, ###this lets you use keyboard navigation
        activestyle = "none",
        takefocus = 0
        )
    tl.pack(fill="both")
   
    def sortbycolumn(table, col):
        """alternate increasing and decreasing order sorts
        """
        order = "-increasing"
        if tl.sortcolumn() == int(col) and tl.sortorder() == "increasing":
            order = "-decreasing"
        tl.sortbycolumn(col, order)
        
    tl.configure(labelcommand = sortbycolumn)
 

    def show():
        print(tl.getcurselection())
    
    b = Button(root, text="Show Selected", command=show)
    b.pack()

    l = Label(root, text="Click the column labels to sort")
    l.pack()


    for a in range(10):
        tl.insert("end", ("Hello " + str((a + 5) % 10), "World " + str(9 - a), str(a)))

    tl.bind('<<TablelistSelect>>', (lambda event: show()))
    root.mainloop()


def edittest():
    """quick test to check if *I* can edit the cells
    
    Selection mode is cell and all columns are editable
    default edit window (entry)
    """
    root = Tk()
    root.title("TableList Edit Test")
    
    tl = TableList(root, 
        background = "white",
        columns = (0, "First", 0, "Second"), 
        selecttype="cell",
        stretch = "all"
        )
    tl.pack(fill="both")
    
    
    for a in range(10):
        tl.insert("end", ("Hello", "World"))
    for col in range(2):
        tl.columnconfigure(col, editable="yes")
    root.mainloop()



def checkbuttontest():
    """on edit show a check button widget
    
    editEndCmd should fill the cell with a 'flag' 
    to show the value (for now just shows 0 or 1)
    """
    def editEndCmd(table, row, col, text):
        print(row, col, text)
        if text:
            return 1
        else:
            return 0

    root = Tk()
    root.title("TableList Edit Test")
    
    tl = TableList(root, 
        background = "white",
        editendcommand=editEndCmd,
        columns = (0, "First", 0, "Second"), 
        selecttype="cell",
        stretch = "all"
        )
    tl.pack(fill="both")
    
    for a in range(10):
        tl.insert("end", (0, "World"))
    tl.columnconfigure(0, editable="yes", editwindow="checkbutton")
    root.mainloop()



if __name__=="__main__":
    tabletest()
    edittest()
    checkbuttontest()
