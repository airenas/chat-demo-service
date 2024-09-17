## Deploy

```mermaid
graph LR
    subgraph policija.lt
        user[User]
        waf[WAF]
        demo[pd-di-chat]
        dipolis_next(pd-di-robot?)
    end
    subgraph VU[VU]
        tran[Vertimas]
    end
    subgraph VDU[VDU]
        tts[Sintezė]
        asr[Atpažinimas]
        dipolis[Chat Robotas]
    end
    user <--> |https| waf
    waf <--> |https| demo
    demo --> |https| tts
    demo --> |https| tran
    demo <--> |wss| asr
    demo <--> |ws| dipolis
    demo <--> |ws| dipolis_next
```    