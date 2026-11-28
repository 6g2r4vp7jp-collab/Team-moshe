# Original soft lo-fi bed for the kitchen reel: 92 BPM, warm keys + gentle kick/hat. Quiet by design (voice on top).
import numpy as np, sys
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR=48000; BPM=76; B=60/BPM; DUR=float(sys.argv[2]) if len(sys.argv)>2 else 60
N=int(DUR*SR)+SR; L=np.zeros(N); R=np.zeros(N); rng=np.random.default_rng(3)
def t_(d): return np.arange(int(d*SR))/SR
def lp(x,f): return sosfilt(butter(2,f,'low',fs=SR,output='sos'),x)
def hp(x,f): return sosfilt(butter(2,f,'high',fs=SR,output='sos'),x)
def add(s,t,g,pan=0):
    i=int(t*SR); s=s[:max(0,N-i)]; L[i:i+len(s)]+=s*g*(1-pan)/1.4; R[i:i+len(s)]+=s*g*(1+pan)/1.4
def key(freqs,d):
    t=t_(d); s=sum(np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*2*f*t)*np.exp(-t*3) for f in freqs)
    return lp(s,2200)*np.exp(-t*0.9)*np.minimum(1,t*60)/len(freqs)
def kick():
    t=t_(0.35); f=50+90*np.exp(-t*25); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
def hat(): t=t_(0.05); return hp(rng.standard_normal(len(t)),7000)*np.exp(-t*90)
def snap():
    t=t_(0.18); return lp(hp(rng.standard_normal(len(t)),1500),5000)*np.exp(-t*30)
ch=[[220.0,261.6,329.6,392.0],[174.6,220.0,261.6,329.6],[261.6,329.6,392.0,493.9],[196.0,246.9,293.7,392.0]]  # Cmaj7 Am7 Fmaj7 G7
bars=int(DUR/(4*B))+1
for b in range(bars):
    t0=b*4*B; c=ch[b%4]
    add(key(c,4*B+0.5),t0,0.55); add(key([c[0]/2],4*B),t0,0.5)
    for q in range(4):
        add(kick(),t0+q*B,0.35 if q==0 and b>1 else 0.0)
        if q in (1,3) and b>1: add(snap(),t0+q*B,0.1)
        for e in (0,0.5): add(hat(),t0+(q+e)*B,0.05 if e else 0.03,0.3)
mix=np.stack([L,R],1)[:int(DUR*SR)]
mix=lp(mix.T,9000).T; fade=int(1.5*SR); mix[:int(0.3*SR)]*=np.linspace(0,1,int(0.3*SR))[:,None]; mix[-fade:]*=np.linspace(1,0,fade)[:,None]
mix/=np.max(np.abs(mix))*1.25
wavfile.write(sys.argv[1],SR,(mix*32767).astype(np.int16)); print('music',DUR)
