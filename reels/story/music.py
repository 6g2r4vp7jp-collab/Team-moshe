# Story version: same original 90 BPM track arranged to 19 bars (~50.7s + tail)
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR=48000; BPM=90; BEAT=60/BPM; BAR=4*BEAT; NB=19
N=int(NB*BAR*SR)+SR*2
L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(7)
def t_(d): return np.arange(int(d*SR))/SR
def add(sig,t,gain=1.0,pan=0.0):
    i=int(t*SR); s=sig[:max(0,N-i)]
    L[i:i+len(s)]+=s*gain*np.sqrt(0.5*(1-pan)); R[i:i+len(s)]+=s*gain*np.sqrt(0.5*(1+pan))
def lp(x,f,o=2): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b,o=2): return sosfilt(butter(o,[a,b],'band',fs=SR,output='sos'),x)
# --- instruments
def kick():
    t=t_(0.5); f=45+120*np.exp(-t*30); ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*np.exp(-t*7); s+=0.6*lp(rng.standard_normal(len(t)),4000)*np.exp(-t*120)
    return np.tanh(s*1.8)
def e808(freq,dur):
    t=t_(dur); f=freq*(1+1.2*np.exp(-t*25)); ph=2*np.pi*np.cumsum(f)/SR
    env=np.minimum(1,t*200)*np.exp(-t*1.1)
    s=np.tanh(2.2*np.sin(ph))*env
    fade=np.ones(len(t)); fl=int(0.03*SR); fade[-fl:]=np.linspace(1,0,fl)
    return lp(s,900)*fade
def snare():
    t=t_(0.45); n=rng.standard_normal(len(t))
    body=np.sin(2*np.pi*190*t)*np.exp(-t*25)
    s=0.8*bp(n,1200,9000)*np.exp(-t*14)+0.7*body
    clap=np.zeros(len(t))
    for k,dl in enumerate([0,0.011,0.022]):
        i=int(dl*SR); clap[i:]+=bp(n[:len(t)-i],900,4000)*np.exp(-t[:len(t)-i]*40)
    return np.tanh(1.5*(s+0.6*clap))
def hat(open_=False):
    t=t_(0.25 if open_ else 0.06); n=rng.standard_normal(len(t))
    return hp(n,7000,4)*np.exp(-t*(12 if open_ else 80))
def boom():
    t=t_(4.0); f=32+60*np.exp(-t*6); ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*np.exp(-t*1.0)
    s+=0.5*lp(rng.standard_normal(len(t)),300)*np.exp(-t*2.5)
    s+=0.35*bp(rng.standard_normal(len(t)),2000,8000)*np.exp(-t*18)
    return np.tanh(1.6*s)
def riser(d):
    t=t_(d); n=rng.standard_normal(len(t))
    out=np.zeros(len(t)); seg=int(0.05*SR)
    for i in range(0,len(t),seg):
        fc=300+ (9000*(i/len(t))**2); out[i:i+seg]=bp(n[i:i+seg],fc,min(fc*2,20000),1)
    return out*(t/d)**2
def whoosh_rev(d):
    s=boom()[:int(d*SR)][::-1]; return s*np.linspace(0,1,len(s))**2
def pad(freqs,d):
    t=t_(d); s=np.zeros(len(t))
    for f in freqs:
        for det in (-0.12,0,0.12):
            s+=np.sign(np.sin(2*np.pi*f*(1+det/100)*t+rng.uniform(0,6)))*0.5+np.sin(2*np.pi*f*t)
    env=np.minimum(1,t/0.8)*np.minimum(1,(d-t)/0.8)
    return lp(s,1400)*env/len(freqs)/4
def pluck(f,d=0.5):
    t=t_(d); s=(np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*2*f*t)+0.25*np.sign(np.sin(2*np.pi*f*t)))*np.exp(-t*6)
    return lp(s,3000)
def string_stab(freqs,d=1.2):
    t=t_(d); s=sum(np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*3*f*t) for f in freqs)
    return lp(s,2500)*np.exp(-t*2.2)*np.minimum(1,t*80)/len(freqs)
# D minor: progression Dm - Bb - Gm - A
roots=[36.71,29.14,24.50,27.50]   # D1, Bb0, G0, A0 -> use *2 for 808
chords=[[146.8,174.6,220.0],[116.5,146.8,174.6],[98.0,116.5,146.8],[110.0,138.6,164.8]]
KICK,SNR,HAT,OH=kick(),snare(),hat(),hat(True)
melody=[293.7,349.2,440.0,392.0,349.2,293.7,261.6,293.7]
def bar_t(b): return b*BAR
# Section map (bar index from 0): 0 intro hit, 1-4 build, 5 slow drop, 6-11 drop, 12 breath/slowmo, 13-15 final, 16 outro
for b in range(NB):
    t0=bar_t(b); ch=b%4
    sect = 'intro' if b==0 else 'build' if b<=4 else 'brk' if b in (5,12) else 'out' if b==NB-1 else 'drop'
    # pads everywhere except outro tail
    if sect!='out': add(pad(chords[ch],BAR+0.6),t0,0.22 if sect!='drop' else 0.26)
    else: add(pad(chords[0],BAR+1.5),t0,0.2)
    if sect=='intro':
        add(boom(),t0,0.9); add(string_stab([73.4,146.8,220.0],2.5),t0,0.6)
        add(e808(roots[0]*2,2.4),t0,0.7)
    if sect=='build':
        for q in range(4):
            add(KICK,t0+q*BEAT,0.55 if q%2==0 else 0.35)
            for e in range(2): add(HAT,t0+q*BEAT+e*BEAT/2,0.12,pan=0.3)
        add(SNR,t0+2*BEAT,0.35+0.08*(b-1))
        for i,f in enumerate(melody[(b%2)*4:(b%2)*4+4]): add(pluck(f*2),t0+i*BEAT,0.13,pan=-0.3)
        if b==4: add(riser(BAR),t0,0.35); add(whoosh_rev(1.2),t0+BAR-1.2,0.5)
    if sect in ('drop',):
        # trap half-time: kick on 1 & 'and of 2', snare on 3
        for kt in (0,1.5*BEAT,2.75*BEAT):
            add(KICK,t0+kt,0.75)
        add(e808(roots[ch]*2,1.5*BEAT-0.02),t0,0.75); add(e808(roots[ch]*2,BEAT*1.2),t0+1.5*BEAT,0.7)
        add(e808(roots[ch]*2*(1.5 if ch==3 else 1),BEAT*1.2),t0+2.75*BEAT,0.65)
        add(SNR,t0+2*BEAT,0.7)
        # hats with rolls
        for s16 in range(16):
            tt=t0+s16*BEAT/4
            if s16%2==0 or b%2==1: add(HAT,tt,0.13 if s16%4==0 else 0.08,pan=0.35)
        if b%2==1:
            for r in range(6): add(HAT,t0+3.5*BEAT+r*BEAT/12,0.07+0.01*r,pan=0.35)
        add(OH,t0+3*BEAT,0.08,pan=-0.35)
        for i,f in enumerate(melody[(b%2)*4:(b%2)*4+4]): add(pluck(f*2),t0+i*BEAT+BEAT/2,0.10,pan=-0.3)
        if b in (6,13): add(boom(),t0,0.7)
        if b==16: add(riser(BAR),t0,0.3)
        if b==11: add(riser(BAR),t0,0.3); add(whoosh_rev(1.2),t0+BAR-1.2,0.5)
        if b==NB-2: add(whoosh_rev(1.2),t0+BAR-1.2,0.55)
    if sect=='brk':
        add(boom(),t0,0.95); add(e808(roots[ch]*2,BAR*0.9),t0,0.7)
        add(string_stab([73.4,110,146.8,174.6],2.6),t0,0.5)
        add(SNR,t0+2*BEAT,0.25); add(riser(BAR*0.5),t0+BAR*0.5,0.25)
        add(whoosh_rev(1.0),t0+BAR-1.0,0.45)
    if sect=='out':
        add(boom(),t0,1.0); add(e808(roots[0]*2,2.6),t0,0.75); add(string_stab([73.4,146.8,220,293.7],3.5),t0,0.55)
mix=np.stack([L,R],1)
mix=mix[:int((NB*BAR+1.8)*SR)]
# gentle glue: soft clip + normalize to -1 dBFS peak
mix=np.tanh(mix*1.1)
fo=int(1.5*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]
mix/=np.max(np.abs(mix))*1.12
wavfile.write(__import__('sys').argv[1],SR,(mix*32767).astype(np.int16))
print('len',len(mix)/SR,'bar',BAR)
