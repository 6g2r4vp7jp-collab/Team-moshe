# Original horror score for the friend video: low drone, dissonant strings, heartbeat, hits on cuts, scream-sting at the end.
import numpy as np, json, sys
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR=48000; DUR=float(sys.argv[2]); N=int(DUR*SR)
cuts=json.load(open(sys.argv[3])); wake=float(sys.argv[4])
rng=np.random.default_rng(13); t=np.arange(N)/SR
def lp(x,f): return sosfilt(butter(2,f,'low',fs=SR,output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),x)
L=np.zeros(N); R=np.zeros(N)
def add(s,at,g,pan=0):
    i=int(at*SR); s=s[:max(0,N-i)]; L[i:i+len(s)]+=s*g*(1-pan); R[i:i+len(s)]+=s*g*(1+pan)
# drone
lfo=0.6+0.4*np.sin(2*np.pi*0.07*t)
dr=sum(np.sin(2*np.pi*f*t+rng.uniform(0,6)) for f in (41.2,41.6,61.7,82.4))
dr+=0.4*lp(np.sign(np.sin(2*np.pi*55*t))*1.0,300)
dr=lp(dr,400)*lfo*np.minimum(1,t/3)
add(dr,0,0.22)
# dissonant high cluster that swells
cl=sum(np.sin(2*np.pi*f*t*(1+0.003*np.sin(2*np.pi*0.3*t+k))) for k,f in enumerate((622.3,659.3,698.5,932.3)))
sw=np.clip((t-4)/(wake-4),0,1)**2
add(lp(cl,3000)*sw*0.7,0,0.05,0.3); add(lp(cl,3000)*sw*0.7,0,0.05,-0.3)
# wind/noise bed
nz=bp(rng.standard_normal(N),300,1800)*(0.5+0.5*np.sin(2*np.pi*0.11*t))
add(nz,0,0.03)
# heartbeat, accelerating towards the wake moment
def thump():
    tt=np.arange(int(0.25*SR))/SR; f=55+40*np.exp(-tt*30); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*14)
bt=3.0
while bt<wake-0.3:
    rate=0.95-0.45*(bt/wake); add(thump(),bt,0.55); add(thump(),bt+0.22,0.38); bt+=rate
# hit on each cut + reverse swell into it
def hit():
    tt=np.arange(int(2.0*SR))/SR; f=38+70*np.exp(-tt*9)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*2.2)+0.5*lp(rng.standard_normal(len(tt)),900)*np.exp(-tt*6)
    return np.tanh(1.8*s)
def swell(d):
    tt=np.arange(int(d*SR))/SR; s=bp(rng.standard_normal(len(tt)),400,5000); return s*(tt/d)**3
for c in cuts[1:]:
    add(swell(0.8),c-0.8,0.12); add(hit(),c,0.35)
# wake sting: screech + big hit
tt=np.arange(int(2.5*SR))/SR
scr=sum(np.sin(2*np.pi*(f+30*np.sin(2*np.pi*7*tt))*tt) for f in (1480,1568,2093))*np.exp(-tt*1.5)
add(swell(1.2),wake-1.2,0.25); add(hit(),wake,0.7); add(lp(scr,6000),wake,0.09,0.2)
# silence just before the sting (tension drop)
g=np.ones(N); a=int((wake-0.45)*SR); b=int(wake*SR); g[a:b]=np.linspace(1,0.05,b-a)
mix=np.stack([L*g,R*g],1)
fo=int(1.5*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]
mix/=np.max(np.abs(mix))*1.12
wavfile.write(sys.argv[1],SR,(mix*32767).astype(np.int16)); print('ok')
