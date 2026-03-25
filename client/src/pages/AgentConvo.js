import {useState,useEffect,useRef} from 'react';
import '../styles/agent-convo.css'
import { Button, Stack, Image, Form, Row, Col, Spinner, InputGroup,FormControl, Modal } from "react-bootstrap";
import { ReactComponent as ReloadIcon } from "../assets/reload.svg";
import { ReactComponent as KeyIcon } from "../assets/key.svg";
import { ReactComponent as LogoutIcon } from "../assets/logout-white.svg";
import { ReactComponent as Bot1Icon } from "../assets/user-1.svg";
import { ReactComponent as Bot2Icon } from "../assets/user-2.svg";
import { ReactComponent as Bot3Icon } from "../assets/user-3.svg";
import { ReactComponent as Bot4Icon } from "../assets/user-4.svg";
import logoImage from '../assets/camelagi.png'
import {ReactComponent as SendIcon} from '../assets/send.svg'
import { ToastContainer, toast } from 'react-toastify';
import {ReactComponent as GoogleIcon} from '../assets/google.svg'
import { ReactComponent as DiscordIcon } from "../assets/discord.svg";
import axios from "axios"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ReactComponent as ShareIcon } from "../assets/share-white.svg";


function AgentConvo() {
    const [isLoggedIn,setIsLoggedIn] = useState(false);
    const [authUrl,setAuthUrl] = useState("")
    const [ranUser1, setRanUser1] = useState(null);
    const [ranUser2, setRanUser2] = useState(null);
    const [started, setStarted] = useState(false);
    const [key, setKey] = useState("");
    const [task, setTask] = useState("");
    const [finished, setFinished] = useState(false);
    const [keyAdded, setKeyAdded] = useState(false);
    const [user, setUser] = useState(false);
    const [role1, setRole1] = useState("");
    const [role2, setRole2] = useState("");
    const [chat,setChat] = useState([])
    const [sessId,setSessId] = useState(0)
    const [showBanner, setShowBanner] = useState(false);
    const [turn,setTurn] = useState(0)
    const [provider, setProvider] = useState("openai");
    const sessionRef = useRef(null)
    sessionRef.current = sessId
    const chatRef = useRef(null)
    chatRef.current = chat
    const turnRef = useRef(null)
    turnRef.current = turn

    let fetchMessages = () => {
        setChat([...chatRef.current,{role:0,msg:null}])
            
        axios.post("/rp/start",{role1:role1,role2:role2,task:task,sessId:sessionRef.current}).then((res)=>{
            setSessId(res.data.sessId)
            if(res.data.convoEnd==true){
                setFinished((prev)=>true)
            }else{
                chatRef.current.at(-1).msg = res.data.userMsg
                setChat([...chatRef.current,{role:1,msg:null}])
                setTimeout(() => {
                    chatRef.current.at(-1).msg = res.data.assistantMsg;
                    setTurn((prev)=>prev+1)
                    startDiscussion(false)
                }, 3000);
                // setUpdate((prev)=>!prev)
                
            }

         })
          .catch((err)=>{
            toast("Failed to respond " + err.response.data);
        })
    }

    let startDiscussion = (newTurn) => {
        let getTurn = turnRef.current
        if(newTurn==true){
            getTurn = 0
            setTurn((prev)=>0)
            setStarted((prev)=>true)
        }
        
        if(getTurn<2){
            fetchMessages()
        }
    }

    const addKey = () => {
        axios.post("/store_key",{key:key,provider:provider}).then((res)=>{
            setKeyAdded(true)
          }).catch((err)=>{
            toast("Key cannot be verified, try again");
        })
    }

    const logout = () => {
        axios.get("/heybot/logout").then((res)=>{
            window.location.reload();
           }).catch((err)=>{
            console.log(err)
           })
    }

    const shareChat = () => {
        navigator.clipboard.writeText(window.location.host+'/conversation/share?session='+sessionRef.current)
		window.open('/conversation/share?session='+sessionRef.current, "_blank");
    }

    useEffect(() => {
        setRanUser1(Math.random())
        setRanUser2(Math.random())
        axios.get("/rp/isLoggedIn").then((res)=>{
            setIsLoggedIn(res.data.isLoggedIn)
            if(res.data.isLoggedIn == false){
                setAuthUrl(res.data.auth_url)
            }else{
                setUser({id:res.data.userId,image:res.data.image})
                if(res.data.provider) setProvider(res.data.provider)
                if(res.data.key_added==null){
                    setKeyAdded((prev)=>false)
                }else{
                    setKeyAdded((prev)=>true)
                    setKey(res.data.key_added)
                }
               
            }
          }).catch((err)=>{
            console.log(err)
        })
		
		window.setTimeout(()=>setShowBanner(true),30000)
    },[])
    useEffect(() => {
        if(document.querySelector('.end-chat')!=null){document.querySelector('.end-chat').scrollIntoView({ behavior: 'smooth', block: 'end' });}
    }, [chat])
    
    return (
        <>
            <div className="agent-convo-container vh-100 d-flex justify-content-center align-items-center">
                <div className="agent-convo-box px-3 py-4 p-md-5 text-white">
                    <div className="d-flex justify-content-between mb-3">
                        <h4><b>CamelAGI</b></h4>
                        {isLoggedIn&&<div className="d-flex gap-3">
                            <ReloadIcon title="New Task" onClick={()=>window.location.reload()} className="icon"/>
							{<KeyIcon title="Change Key" onClick={()=>setKeyAdded(false)} className="icon"/>}
                            <LogoutIcon title="Logout" onClick={logout} className="icon"/>
                        </div>}
                    </div>
                    {isLoggedIn?
                    <Stack className="scroll-container " gap={3}>
                        {keyAdded?
                            <>
                                {started?
                                    <>
                                        <Stack className="agent-scroll" gap={3}>
                                            {chatRef.current.length>0&&chatRef.current.map((message)=>
                                                message.role==0?
                                            <div className="d-flex align-items-end align-self-start me-4 role1-container">
                                                {ranUser1!=null&&ranUser1>0.5?<Bot1Icon className="agent-chat-icon"/>:<Bot2Icon className="agent-chat-icon"/>}
                                                <div className="d-flex flex-column gap-1">
                                                    <div className="bubble agent-1-chat ">
                                                        {message.msg==null?
                                                        <Stack className="p-2 loading" direction="horizontal" gap={2}>
                                                            <Spinner size="sm" animation="grow" />
                                                            <Spinner size="sm" animation="grow" />
                                                            <Spinner size="sm" animation="grow" />
                                                        </Stack>:
                                                        <p className="p-2 m-0 agent-msg-container"><ReactMarkdown children={message.msg} remarkPlugins={[remarkGfm]} /></p>}
                                                    </div>
                                                    <small className="role-name ms-2 align-self-start">{role1}</small>
                                                </div>
                                            </div>:
                                            <div className="d-flex align-items-end align-self-end ms-4 role2-container">
                                                <div className="d-flex flex-column gap-1">
                                                    <div className="bubble agent-2-chat ">
                                                        {message.msg==null?
                                                        <Stack className="p-2 loading" direction="horizontal" gap={2}>
                                                            <Spinner size="sm" animation="grow" />
                                                            <Spinner size="sm" animation="grow" />
                                                            <Spinner size="sm" animation="grow" />
                                                        </Stack>:
                                                        <p className="p-2 m-0 agent-msg-container"><ReactMarkdown children={message.msg} remarkPlugins={[remarkGfm]} /></p>}
                                                    </div>
                                                    <small className="role-name me-2 align-self-end">{role2}</small>
                                                </div>
                                                {ranUser2!=null&&ranUser2>0.5?<Bot3Icon className="agent-chat-icon"/>:<Bot4Icon className="agent-chat-icon"/>}
                                            </div>
                                            )}
                                            {sessionRef.current!=0&&<Button className="align-self-end agent-share-btn" onClick={shareChat}><ShareIcon className="small-icon me-1"/><small>Share</small></Button>}
                                            <div className="end-chat"></div>
                                        </Stack>
                                        {finished?
                                            <h5><b>Task Completed!</b></h5>
                                        :
                                        <>
                                            {turnRef.current<3?
                                                <Button className="continue-button mt-auto d-flex gap-2 justify-content-center align-items-center" disabled><Spinner size="sm"/>Loading</Button>
                                                :<Button className="continue-button mt-auto" onClick={()=>startDiscussion(true)}>Continue</Button>}
                                        </>}
                                    </>
                                :
                                    <>
                                        <h5 className="m-0">Get started with a task to discuss</h5>
                                        <Form.Group className=" mt-4" >
                                            <Form.Label >Enter Role of the Instructor</Form.Label>
                                            <Form.Control className="agent-input" value={role1} placeholder="Stock Trader" onChange={(e)=>setRole1(e.target.value)}/>
                                        </Form.Group>
                                        <Form.Group className=" " >
                                            <Form.Label >Enter Role of the Assistant</Form.Label>
                                            <Form.Control className="agent-input" value={role2} placeholder="Python Programmer" onChange={(e)=>setRole2(e.target.value)}/>
                                        </Form.Group>
                                        <Form.Group className=" " >
                                            <Form.Label >Enter topic of discussion</Form.Label>
                                            <Form.Control className="agent-input" value={task}  placeholder="Develop a trading bot for the stock market" onChange={(e)=>setTask(e.target.value)}/>
                                        </Form.Group>
										<Button className="continue-button mt-auto" onClick={()=>startDiscussion(true)}>Start Discussion</Button>
                                    </>
                                
                                }
                            </>:
                            <Stack className="align-items-center" gap={3}>
                                <h6><b>Add your API Key</b></h6>
                                <Form.Group className="w-100">
                                    <Form.Label>LLM Provider</Form.Label>
                                    <Form.Select className="agent-input" value={provider} onChange={(e)=>{setProvider(e.target.value);setKey("")}}>
                                        <option value="openai">OpenAI</option>
                                        <option value="minimax">MiniMax</option>
                                    </Form.Select>
                                </Form.Group>
                                <p><small>{provider==="minimax" ? "Get your MiniMax API Key from the MiniMax platform." : "Get your OpenAI Key by signing up/ logging in from the OpenAI Dashboard."} </small>
                                {provider==="minimax" ? <a target="_blank" rel="noreferrer" href="https://platform.minimaxi.com/">Go to MiniMax Platform</a> : <a target="_blank" rel="noreferrer" href="https://platform.openai.com/account/api-keys">Go to Dashboard</a>}</p>
                                <InputGroup >
                                    <FormControl className="chat-input px-md-5 py-md-2 shadow-none"
                                    style={{height:'48px'}}
                                    value={key}
                                    onChange={(e)=>setKey(e.target.value)}
                                    onKeyDown={(e)=>{e.code=="Enter"&&addKey()}}
                                    />
                                    <Button variant="outline-secondary" className="chat-button text-dark fw-bold ps-md-3 pe-md-5 py-md-2" onClick={addKey}>
                                        <SendIcon className="icon"/>
                                    </Button>
                                </InputGroup>
                                <small>Watch this video to get started</small>
                                <iframe className="key-video-agent" src="https://www.youtube.com/embed/FaJdwbNWNkk" title="YouTube video player" frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowFullScreen></iframe>
                            </Stack>
                        }
                    </Stack>:
                    <Stack className="align-items-center" gap={4}>
                         <Image className="logo mt-5 pt-5" src={logoImage}/>
                            {/* <h5 className="">Login to agi</h5> */}
                            <h5 className="">Accomplish your task with AI agents</h5>
                            <Button className="option-buttons px-3 py-2 align-self-center" href={authUrl}> Login with Google</Button>
                            <Button className="option-buttons px-3 py-2 align-self-center" href="https://github.com/SamurAIGPT/Camel-AutoGPT/" target="_blank">Star CamelAGI on Github</Button>							
                            {/* <Stack direction="horizontal" gap={2} style={{cursor:'pointer',opacity:'0.7'}} className="mt-auto align-self-center" onClick={()=>navigate('/agi/faq')}><QuestionIcon className="icon"/> <b>Know More</b></Stack> */}
                    </Stack>
                    }
                </div>
                <ToastContainer />
                <Modal className="banner-modal" centered show={showBanner} onHide={()=>setShowBanner(false)}>
                <Modal.Body className="p-5 position-relative">
                <b style={{cursor:'pointer'}} onClick={()=>setShowBanner(false)} className="position-absolute top-0 end-0 me-4 mt-2">X</b>
                <Stack className="align-items-center" gap={3}>
                    <a href="https://www.producthunt.com/posts/camel-agi?utm_source=badge-featured&utm_medium=badge&utm_souce=badge-camel&#0045;agi" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=389872&theme=light" alt="Camel&#0032;AGI - Communicative&#0032;Agents&#0032;on&#0032;GPT | Product Hunt" /></a>                    
                    <a className="discord-invite px-3 py-3 ms-3" target="_blank" href="https://discord.gg/A6EzvsKX4u"><DiscordIcon className="icon me-1"/> Join Our Discord</a>
                    <a className="discord-invite px-3 py-3 ms-3" target="_blank" href="https://github.com/SamurAIGPT/Camel-AutoGPT/">Star CamelAGI on Github</a>
                </Stack>
                </Modal.Body>
            </Modal> 				
            </div>
        </>
    )

}

export default AgentConvo;