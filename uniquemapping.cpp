#include<cmath>
#include<iostream>
#include<vector>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#define PI 3.141592
#define TOLERANCE 0.00005
// #define DIST 0.0004
// #define TEETA 0.70
// #define disp std::cout<<
// void debugpri(*a);
namespace py = pybind11;

double distance(double a1,double b1,double a2,double b2){
    // return abs(a1-a2)+abs(b1-b2);
    double da,db,c;
    a1*=(PI/180);
    a2*=(PI/180);
    b1*=(PI/180);
    b2*=(PI/180);
    da=a1-a2;
    db=b1-b2;
    c =pow(sin(da/2),2)+cos(a1)*cos(a2) * pow(sin(db/2),2);
    c=2*atan2(sqrt(c),sqrt(1-c))*6371;
    
    return c;

}

double angle(double *y, double *x){
    double ang = abs(*y-*x);
    return std::min(ang,2*PI-ang);
}



class lineSegment{
    private:
        double m,c,rt1plusm2;
        double LT[2],LN[2];
        double C2,X,Y,dy;
    public:
        double teeta,xa,xb,ya,yb;
        std:: string vname;
        int strf,endf;
        // std::string v;
        lineSegment(double xa,double ya,double xb ,double yb, std:: string & vname, int strf,int endf)
        : xa(xa), ya(ya), xb(xb), yb(yb), vname(vname), strf(strf), endf(endf)
        {
	        // this->xa=xa;this->ya=ya;
            if (xb - xa == 0 ) xb+=0.00001;
            if (yb - ya == 0 ) yb+=0.00001;
            m = (yb - ya) / (xb - xa);
            teeta = atan2((yb - ya),(xb - xa));
            c = ya - m * xa;
            rt1plusm2 = sqrt(1 + m*m);
            if (xb<xa){
                LT[0]=xa;LT[1]=xb;
            }
            else {
                LT[0]=xb;LT[1]=xa;
            }
            if (yb < ya){
                LN[0] = ya;LN[1]=yb;
            }
            else{
                LN[0] = yb;LN[1]=ya;
            }
            LT[1]-=TOLERANCE;
            LN[1]-=TOLERANCE;
            LN[0]+=TOLERANCE;
            LT[0]+=TOLERANCE;
        }
        void project(double * arr){
            C2 = arr[2] - m * arr[1];
            arr[0] = (C2-c)/rt1plusm2;
            dy = arr[0]/rt1plusm2;
            arr[2] = arr[2] - dy;
            arr[1] = (arr[2]-c)/m;
            
            // arr[2]=Y;
            
        }
        bool validate(double *arr){
            if (LT[1] <= arr[1] && arr[1] <= LT[0] && LN[1] <= arr[2] && arr[2] <= LN[0]){
                return true;
            }
            return false;
        }
        
        bool validate_merge(double*A, double* B){
            if (abs(B[1] - xa) >= abs(A[1] - xa) && abs(B[2] - ya) >=  abs(A[2] - ya)){
                return true;
            }
            return false;
        }
        

};

class maps{
    public :
    std::vector <lineSegment*> unique,dupli;
    lineSegment *sega,*segb;
    double TEETA=0.7,DIST=0.00035;
    double A[3];
    double B[3];
    py::list overl ; //
    maps(double dist,double teeta) : TEETA(teeta), DIST (dist) {}
    ~maps(){
        for (auto & i : unique){delete i;}
        for (auto & i : dupli){delete i;}

    }
    py::array_t<double> uniq2pyarray(){
        std::vector<size_t> shape = {unique.size(),4};
        return py::array_t<double>(shape,uniquetoarray());
    }
    py::list get(){py::list f (overl); return f;}
    py::tuple getall(){
        py::dict v;
        py::list unq,dup;
        for (const auto &i : unique) {

            unq.append(py::make_tuple(i->xa, i->ya, i->xb, i->yb, i->vname, i->strf, i->endf));
        }

        for (const auto &i : dupli) {

            dup.append(py::make_tuple(i->xa, i->ya, i->xb, i->yb, i->vname, i->strf, i->endf));
        }
        return py::make_tuple(unq,dup);

    }
    
    double * uniquetoarray(){
        double * arr = new double [unique.size()*4];
        double * t=arr;
        for(auto &i:unique){
            t[0]=i->xa;
            t[1]=i->ya;
            t[2]=i->xb;
            t[3]=i->yb;
            t=t+4;
        }
        return arr;
    }
    
    bool addline(double xa,double ya,double xb,double yb, std::string & vname, int strf,int endf){
        int i,j;
        lineSegment* currentseg = new lineSegment( xa, ya, xb,yb,vname , strf,endf);
        /////
        if ((abs(xa-xb)+abs(ya-yb)) < (DIST/8)){
            unique.push_back(currentseg);
            return true;
        }
        /////

        for( i =0;i<unique.size();i++){
            A[1]=xa;A[2]=ya;
            
            sega = unique[i];
            sega->project(A);
            // std::cout<<"%%%%%$$\n"<<A[0]<<"*"<<sega->validam.te(A);
            if  (abs(A[0])< DIST && sega->validate(A) && angle(&sega->teeta,&currentseg->teeta) < TEETA){
                
                for(j=i;j<unique.size();j++){
                    B[1]=xb;B[2]=yb;
                    segb = unique[j];
                    segb->project(B);
                    if  (abs(B[0])< DIST && segb->validate(B) && angle(&segb->teeta,&currentseg->teeta) < TEETA){
                        if (sega->validate_merge(A,B)){
                            // delete currentseg;
                            dupli.push_back(currentseg);
                            overl.append(currentseg->vname);
                            overl.append(segb->vname);
                            overl.append(sega->vname);
                            return false;
                        }
                        
                    }
                }
            }
        }
        unique.push_back(currentseg);
        return true;
        
    }
    
    
};


PYBIND11_MODULE(uniquemapping,m ) { // cpp_sort is module name , m is interface for binding  
    py::class_<maps>(m, "maps") // exposes the class to python as cpp_ 
        .def(py::init<double , double>()) //  expose the class constructor function,  array as input
        .def("addline", &maps::addline) // expose the heapsort function from cpp_ class
        .def("get",&maps::get)
        .def("getall",&maps::getall);
    m.def("distance",&distance);
    // py::class
        // .def_readwrite("array_size", &cpp_::n); //expose variable n,  rename as array_size

}

//c++ -O3 -Wall -shared -std=c++11 -fPIC $(python3 -m pybind11 --includes) uniquemapping.cpp -o uniquemapping$(python3-config --extension-suffix)

// int main()
// {   double i,j,k,l;
//     i=1;j=1;k=1;l=4;
//     maps m(0.1,1);
//     std::cout<<m.addline(i,j,k,l)<<"#";
//     i=1;j=1.01;k=1;l=4;
//     std::cout<<m.addline(i,j,k,l)<<"@";
    

//     std::cout<<m.unique.size();

//     return 0;
// }
