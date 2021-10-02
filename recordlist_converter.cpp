#include <bits/stdc++.h>
#define DEBUG true
using namespace std; // 不规范不过反正也不维护了就这样吧233
map<string,string> pinyinToCharacter;
string try_convert(string s){
    string ret;
//    for(int i=0;i<s.size();++i){
//        if(s[i]>='A'&&s[i]<='Z') s[i]-=32;
//    }
    string tmp;
    for(int i=0;i<s.size();++i){
        if(isalpha(s[i])) tmp+=s[i];
        if((!isalpha(s[i])||i+1==s.size())&&!tmp.empty()){
            if(pinyinToCharacter[tmp].empty()) return string("");
            else ret+=pinyinToCharacter[tmp]; 
            tmp.clear();
        }
    }
    return ret;
}
int main(int argc,char *argv[]){
    if(argc!=2&&!DEBUG){return puts("Usage: recordlist_converter {recordlist}\n\tExample: > recordlist_converter riskuCVVC_1016.txt"),1;}
    
    FILE *fp_pinyin_lib=fopen("pinyin_library.txt","r");
    if(fp_pinyin_lib==NULL) return puts("pinyin_library.txt not found. download it from github or generate it from 'pinyin_library_generator.py'."),1;
    
    // init pinyin library
    char ch;
    while(ch!=EOF){ // 硬编码但是别在意啦反正也不会去维护了
        string hans,pinyin; ch=fgetc(fp_pinyin_lib);
        hans+=ch; ch=fgetc(fp_pinyin_lib);
        hans+=ch; ch=fgetc(fp_pinyin_lib);
        while(ch!='\n'&&ch!=EOF){
            pinyin+=ch;
            ch=fgetc(fp_pinyin_lib);
        }
        if(pinyinToCharacter[pinyin].empty()) pinyinToCharacter[pinyin]=hans;
    }

    fclose(fp_pinyin_lib);

    fstream fs_recordlist(DEBUG?"riskuCVVC_1016.txt":argv[1]); string tmp;
    while(fs_recordlist>>tmp){
        string ret=try_convert(tmp);
        if(!ret.empty()){
            ofstream out_result((string)"output\\"+tmp+".txt");
            out_result<<ret;
            out_result.flush();
        }
    }
}
