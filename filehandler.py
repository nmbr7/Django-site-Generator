import lxml.html as html
import lxml,re
import io

# linestr is a list of keywords to search in the file in sequence eg: `htmlfindline(filename,['input','name'])`
def htmlfind_and_replace(fileloc,linestr,newline=None,insert=None):
    root = html.parse(fileloc).getroot()
    tag_list = lxml.etree.tostring(root,pretty_print=True).decode('utf-8').strip('&#13;').split('\n')
    reg = re.compile(' *')
    lines = []
    for count,line in enumerate(tag_list):
        result = all(i in line for i in linestr)
        if result:
            if newline:
                #yield(result)
              #  print("Index : {} {}".format(count,line))
                l = reg.match(line).end()
                intent = l*' ' if l != 0 else 20*' '
                tag_list[count] = "{}{}".format(intent,newline)
              #  print("Index : {}:{} {}".format(count,len(intent),tag_list[count]))
                #fw = open('New.html','w')
                fw = io.open(fileloc,'w',encoding='utf-8')
                for i in tag_list:
                    fw.write(i.strip('&#13;')+'\n')
                fw.close()
                return count
            elif insert:
                lines.append((count,line))
            else:
                lines.append((count,line))
#    print(lines)
    if insert:
        for count,line in lines:
            intent = ' '*reg.match(line).end()
            tag_list.insert(count,"{}{}".format(intent,insert))
            fw = io.open(fileloc,'w',encoding='utf-8')
            for i in tag_list:
                fw.write(i.strip('&#13;')+'\n')
            fw.close()
    return lines


#Writing python django files
def django_write(fileloc,string,tt='a'):
    fh = open(fileloc, tt)
    fh.write('\n'+string)
    fh.close()

#For parsing django `Settings` File
def python_findline(fileloc,linestr):
    fd = open(fileloc,'r')
    tag = insert = line_no = sameline = 0
    for count,line in enumerate(fd.readlines()):
        if linestr in line:
            insert = count
            line_no = count
            if '[' in line:
                tag=1
        if tag == 1 and ( ']' in line ):
            if len(line) == 2:
                insert = count
                tag = 0
            if line_no == count:
                line
                tag = 0
                sameline=1
            break
    return {'line_no' : line_no ,'Insert' : insert,'Sameline' : sameline}

#For parsing django `Settings` File
def python_writeline(fileloc,data,lineno,replace=None):
    read_fd = open(fileloc,'r')
    lines = read_fd.readlines()
    read_fd.close()
    write_fd = open(fileloc,'w')
    if replace:
        lines[lineno] = data
    else:
        lines.insert(lineno,data)
    write_fd.writelines(lines)
    write_fd.close()
