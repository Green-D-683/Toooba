`include "ProcConfig.bsv"
import Types::*;
import ProcTypes::*;
import ReservationStationEhr::*;
import ReservationStationAlu::*;
import ReservationStationFpuMulDiv::*;
import ReservationStationMem::*;
import SynthParam::*;
import BrPred::*;
import DirPredictor::*;
import SpecFifo::*;

`ifdef IN_ORDER

typedef union tagged {
    ToReservationStation#(AluRSData) AluExe;
    ToReservationStation#(FpuMulDivRSData) FpuMulDivExe;
    ToReservationStation#(MemRSData) MemExe;
} InOrderPipelineData deriving(Bits, Eq, FShow);

// ReservationStation's are OOO, use SpecFifo instead?

typedef SpecFifo#( // Probably size 2 here
    2, InOrderPipelineData,
    2,
    2 
) InOrderPipeline;
module mkInOrderPipeline(InOrderPipeline);
    let sched = SpecFifoSched {
        validDeqPort: 0,
        validEnqPort: 1,
        validWrongSpecPort: 0,
        sbDeqPort: 0,
        sbEnqPort: 0,
        sbWrongSpecPort: 0,
        wrongSpec_conflict_enq: True,
        wrongSpec_conflict_deq: True,
        wrongSpec_conflict_canon: True // acutally canon never fire
    };
    InOrderPipeline m <- mkSpecFifo(sched, `RS_LAZY_ENQ);
    return m;
endmodule

`endif 

// ! SpecFifo vs ReservationStation for reference

// interface SpecFifo#(
//     numeric type size, type t,
//     numeric type validPortNum, // valid EHR port num
//     numeric type sbPortNum // specBits EHR port num
// );
//     method Action enq(ToSpecFifo#(t) x); // Equivalent
//     method Bool notFull; // Equivalent to canEnq?
//     method Action deq; Equivalent to doDispatch
//     method ToSpecFifo#(t) first; Equivalent to dispatchData
//     method Bool notEmpty; 
//     interface SpeculationUpdate specUpdate; Equivalent
// endinterface

// interface ReservationStation#(
//     numeric type size, numeric type setRegReadyNum, type a
// );
//     method Action enq(ToReservationStation#(a) x);
//     method Bool canEnq;

//     method Action setRobEnqTime(InstTime t); Not needed - only used for findOldest
//     method ToReservationStation#(a) dispatchData;
//     method Action doDispatch;

//     interface Vector#(setRegReadyNum, Put#(Maybe#(PhyRIndx))) setRegReady; Not needed - OOO Scheduling

//     // For count-based scheduling when there are multiple reservation stations
//     // for the same inst type. This method only takes effect when module
//     // parameter countValid is true.
//     method Bit#(TLog#(TAdd#(size, 1))) approximateCount;

//     // performance: count full cycles
//     method Bool isFull_ehrPort0; negate notFull?

//     interface SpeculationUpdate specUpdate;
// endinterface

// ! OOO RS's for reference:

// // ALU pipeline is aggressive, i.e. it recv bypass and early RS wakeup
// typedef ReservationStation#(`RS_ALU_SIZE, WrAggrPortNum, AluRSData) ReservationStationAlu;
// (* synthesize *)
// module mkReservationStationAlu(ReservationStationAlu);
//     ReservationStationAlu m <- mkReservationStation(`LAZY_RS_RF, `RS_LAZY_ENQ, valueof(AluExeNum) > 1);
//     return m;
// endmodule

// // FPU MUL DIV pipeline is aggressive, i.e. it recv bypass and early RS wakeup
// typedef ReservationStation#(`RS_FPUMULDIV_SIZE, WrAggrPortNum, FpuMulDivRSData) ReservationStationFpuMulDiv;
// (* synthesize *)
// module mkReservationStationFpuMulDiv(ReservationStationFpuMulDiv);
//     let m <- mkReservationStation(`LAZY_RS_RF, `RS_LAZY_ENQ, valueof(FpuMulDivExeNum) > 1);
//     return m;
// endmodule

// // MEM pipeline is aggressive, i.e. it recv bypass and early RS wakeup
// typedef ReservationStation#(`RS_MEM_SIZE, WrAggrPortNum, MemRSData) ReservationStationMem;
// (* synthesize *)
// module mkReservationStationMem(ReservationStationMem);
//     let m <- mkReservationStation(`LAZY_RS_RF, `RS_LAZY_ENQ, False);
//     return m;
// endmodule