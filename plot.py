import reveallib
import reveallib64
from utils import *

try:
    from matplotlib import pyplot as plt
    from matplotlib import patches as patches
except:
    pass

def plot(args):
    #from matplotlib import pyplot as plt
    vertgaps=[]
    horzgaps=[]
    vertgapsizes=[]
    horzgapsizes=[]
    qrylength=0
    reflength=0
    ax = plt.axes()
    if len(args.fastas)==2:
        #get mmems for forward orientation
        if args.sa64:
            idx=reveallib64.index()
        else:
            idx=reveallib.index()

        for sample in args.fastas:
            idx.addsample(sample)
            for name,seq in fasta_reader(sample,truncN=False):
                intv=idx.addsequence(seq.upper())
                break #expect only one sequence per fasta for now
        idx.construct()
        
        if args.uniq:
            print "Extracting mums..."
            mmems=[(mem[0],mem[1],mem[2],0) for mem in idx.getmums(args.minlength)]
        else:
            print "Extracting mems..."
            mmems=[(mem[0],mem[1],mem[2],0,mem[3]) for mem in idx.getmems(args.minlength)]
        print "done."
        
        sep=idx.nsep[0]
        
        #get mmems for reverse orientation
        if args.sa64:
            idx=reveallib64.index()
        else:
            idx=reveallib.index()
        
        sample=args.fastas[0]
        idx.addsample(sample)
        for name,seq in fasta_reader(sample,truncN=False):
            pc=None
            gapsize=None
            for i,c in enumerate(seq):
                if c=='N' and pc!='N':
                    horzgaps.append(i)
                    gapsize=1
                elif c=='N' and pc=='N':
                    gapsize+=1
                elif c!='N' and pc=='N':
                    horzgapsizes.append(gapsize)
                pc=c
            reflength+=len(seq)
            intv=idx.addsequence(seq.upper())
            break #expect only one sequence per fasta for now
        
        sample=args.fastas[1]
        idx.addsample(sample)
        for name,seq in fasta_reader(sample,truncN=False):
            pc=None
            gapsize=None
            for i,c in enumerate(seq):
                if c=='N' and pc!='N':
                    vertgaps.append(i)
                    gapsize=1
                elif c=='N' and pc=='N':
                    gapsize+=1
                elif c!='N' and pc=='N':
                    vertgapsizes.append(gapsize)
                pc=c
            qrylength+=len(seq)
            intv=idx.addsequence(rc(seq.upper()))
            break #expect only one sequence per fasta for now
        idx.construct()
        
        if args.uniq:
            print "Extracting RC mums..."            
            mmems+=[(mem[0],mem[1],mem[2],1) for mem in idx.getmums(args.minlength)]
        else:
            print "Extracting RC mems..."            
            mmems+=[(mem[0],mem[1],mem[2],1,mem[3]) for mem in idx.getmems(args.minlength)]
        print "done."
    
    elif len(args.fastas)==1:
        
        if args.sa64:
            idx=reveallib64.index()
        else:
            idx=reveallib.index()
        
        sample=args.fastas[0]
        idx.addsample(sample)
        for name,seq in fasta_reader(sample, truncN=False):
            pc=None
            gapsize=None
            for i,c in enumerate(seq):
                if c=='N' and pc!='N':
                    horzgaps.append(i)
                    gapsize=1
                elif c=='N' and pc=='N':
                    gapsize+=1
                elif c!='N' and pc=='N':
                    horzgapsizes.append(gapsize)
                pc=c
            reflength+=len(seq)
            intv=idx.addsequence(seq.upper())
            break #expect only one sequence per fasta for now
        
        sample=args.fastas[0]
        idx.addsample(sample)
        ls=0
        for name,seq in fasta_reader(sample, truncN=False):
            pc=None
            gapsize=None
            for i,c in enumerate(seq):
                if c=='N' and pc!='N':
                    vertgaps.append(i)
                    gapsize=1
                elif c=='N' and pc=='N':
                    gapsize+=1
                elif c!='N' and pc=='N':
                    vertgapsizes.append(gapsize)
                pc=c
            qrylength+=len(seq)
            intv=idx.addsequence(rc(seq.upper()))
            break #expect only one sequence per fasta for now
        idx.construct()
        sep=idx.nsep[0]
        
        if args.uniq:
            mmems=[(mem[0],mem[1],mem[2],1) for mem in idx.getmums(args.minlength) if mem[0]>args.minlength]
        else:
            mmems=[(mem[0],mem[1],mem[2],1,mem[3]) for mem in idx.getmems(args.minlength) if mem[0]>args.minlength]
        
    else:
        logging.fatal("Can only create mumplot for 2 sequences or self plot for 1 sequence.")
        return
    
    if args.region!=None:
        start,end=args.region.split(":")
        start=int(start)
        end=int(end)
    else:
        start=0
        end=idx.nsep[0]
    
    del idx

    print "Drawing",len(mmems),"matches."
    
    #pos=args.pos
    #dist=args.env
    
    for mem in mmems:
        sps=sorted(mem[2])
        l=mem[0]
        sp1=sps[0]
        sp2=sps[1]-sep
        ep1=sp1+l
        ep2=sp2+l
        
        if sp1>start and ep1<end:
            if mem[3]==0:
                if args.uniq:
                    plt.plot([sp1,ep1],[sp2,ep2],'r-')
                else:
                    if mem[4]==0: #non-uniq
                        plt.plot([sp1,ep1],[sp2,ep2],'y-')
                    else:
                        plt.plot([sp1,ep1],[sp2,ep2],'r-')
            else:
                if args.uniq: #only uniq matches in the list
                    plt.plot([sp1,ep1],[qrylength-sp2,qrylength-ep2],'g-')
                else:
                    if mem[4]==0: #non-uniq
                        plt.plot([sp1,ep1],[qrylength-sp2,qrylength-ep2],'y-')
                    else:
                        plt.plot([sp1,ep1],[qrylength-sp2,qrylength-ep2],'g-')
    
    del mmems

    for p,l in zip(horzgaps,horzgapsizes):
        ax.add_patch(
            patches.Rectangle(
                (p, 0), #bottom left
                l, #width
                qrylength, #height
                alpha=.25
            )
        )
     
    for p,l in zip(vertgaps,vertgapsizes):
        ax.add_patch(
            patches.Rectangle(
                (0, p), #bottom left
                reflength, #width
                l, #height
                alpha=.25
            )
        )
    
    plt.title(" vs. ".join(args.fastas))
    if len(args.fastas)==2:
        plt.xlabel(args.fastas[0])
        plt.ylabel(args.fastas[1])
    else:
        plt.xlabel(args.fastas[0])
        plt.xlabel(args.fastas[0]+"_rc")
    plt.autoscale(enable=False)
    
    if args.region!=None:
        start,end=args.region.split(":")
        plt.axvline(x=int(start),linewidth=3,color='b',linestyle='dashed')
        plt.axvline(x=int(end),linewidth=3,color='b',linestyle='dashed')
    
    if args.interactive:
        plt.show()
    else:
        b1=os.path.basename(args.fastas[0])
        b2=os.path.basename(args.fastas[1])
        fn1=b1[0:args.fastas[0].rfind('.')] if b1.find('.')!=-1 else b1
        fn2=b2[0:args.fastas[1].rfind('.')] if b2.find('.')!=-1 else b2
        plt.savefig(fn1+"_"+fn2+".png")
